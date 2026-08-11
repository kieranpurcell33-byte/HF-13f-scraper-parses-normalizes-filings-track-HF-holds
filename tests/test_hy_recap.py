"""Tests for the hy_recap daily high-yield recap pipeline."""

from datetime import date

import pytest

from hy_recap import RecapBuilder, RecapConfig, render_markdown
from hy_recap.calendar_util import (
    is_trading_day,
    next_trading_day,
    previous_trading_day,
)
from hy_recap.delivery import output_filename, write_recap
from hy_recap.models import Direction


# --- Trading calendar ------------------------------------------------------

def test_weekend_is_not_a_trading_day():
    assert not is_trading_day(date(2026, 8, 8))   # Saturday
    assert not is_trading_day(date(2026, 8, 9))   # Sunday
    assert is_trading_day(date(2026, 8, 10))      # Monday


def test_previous_trading_day_skips_weekend():
    # Monday 2026-08-10 -> previous session is Friday 2026-08-07
    assert previous_trading_day(date(2026, 8, 10)) == date(2026, 8, 7)


def test_next_trading_day_skips_weekend():
    # Friday 2026-08-07 -> next session is Monday 2026-08-10
    assert next_trading_day(date(2026, 8, 7)) == date(2026, 8, 10)


def test_holiday_is_skipped():
    # 2026-01-01 New Year's Day is a full-close holiday.
    assert not is_trading_day(date(2026, 1, 1))
    # Independence Day 2026 falls on Saturday -> observed Friday 7/3.
    assert not is_trading_day(date(2026, 7, 3))


def test_good_friday_is_a_holiday():
    # Good Friday 2026 = 2026-04-03.
    assert not is_trading_day(date(2026, 4, 3))


# --- Builder ---------------------------------------------------------------

def test_build_previous_trading_day_from_reference():
    report = RecapBuilder().build(as_of=date(2026, 8, 11))  # Tuesday
    assert report.session_date == date(2026, 8, 10)         # Monday
    assert report.outlook.next_session_date == date(2026, 8, 11)


def test_build_explicit_date():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    assert report.session_date == date(2026, 8, 10)
    assert report.top_performers and report.bottom_performers
    assert report.top_performers[0].direction == Direction.GAINER
    assert report.bottom_performers[0].direction == Direction.DECLINER


def test_sample_report_flags_synthetic_data():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    assert any("SAMPLE" in c.upper() for c in report.data_caveats)


def test_executive_summary_mentions_index_move():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    assert "%" in report.executive_summary


# --- Rendering -------------------------------------------------------------

def test_render_markdown_has_all_four_sections():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    md = render_markdown(report)
    assert "Notable events & news" in md
    assert "Best & worst performing HY bonds" in md
    assert "Market context" in md
    assert "Expected for the next trading day" in md


def test_render_markdown_is_nonempty_and_dated():
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    md = render_markdown(report)
    assert md.startswith("# US High Yield Daily Recap")
    assert "August 10, 2026" in md
    # List items should be on separate lines (whitespace-control regression guard).
    assert "[(sample)]\n" in md


# --- Config & delivery -----------------------------------------------------

def test_config_defaults_to_sample():
    cfg = RecapConfig()
    assert cfg.bond_source == "sample"
    assert cfg.missing_credentials() == []


def test_config_reports_missing_rest_credentials(monkeypatch):
    monkeypatch.setenv("HY_BOND_SOURCE", "rest")
    monkeypatch.delenv("HY_REST_BASE_URL", raising=False)
    cfg = RecapConfig()
    assert "HY_REST_BASE_URL" in cfg.missing_credentials()


def test_output_filename_format():
    assert output_filename(date(2026, 8, 10)) == "hy_recap_2026-08-10.md"


def test_write_recap_roundtrip(tmp_path):
    report = RecapBuilder().build(session_date=date(2026, 8, 10))
    md = render_markdown(report)
    path = write_recap(md, report.session_date, output_dir=str(tmp_path))
    assert path.exists()
    assert path.read_text(encoding="utf-8") == md


def test_unknown_source_raises(monkeypatch):
    monkeypatch.setenv("HY_MACRO_SOURCE", "does-not-exist")
    with pytest.raises(ValueError):
        RecapBuilder(config=RecapConfig())


# --- Google Drive delivery -------------------------------------------------

class _FakeExecutable:
    def __init__(self, result):
        self._result = result

    def execute(self):
        return self._result


class _FakeFiles:
    def __init__(self, recorder):
        self.recorder = recorder

    def create(self, **kwargs):
        self.recorder["create"] = kwargs
        return _FakeExecutable({
            "id": "fake-id-123",
            "name": kwargs["body"]["name"],
            "webViewLink": "https://drive.google.com/file/d/fake-id-123",
        })


class _FakePermissions:
    def __init__(self, recorder):
        self.recorder = recorder

    def create(self, **kwargs):
        self.recorder.setdefault("permissions", []).append(kwargs)
        return _FakeExecutable({"id": "perm-1"})


class _FakeDriveService:
    def __init__(self):
        self.recorder = {}

    def files(self):
        return _FakeFiles(self.recorder)

    def permissions(self):
        return _FakePermissions(self.recorder)


def _write_sample_md(tmp_path, session=date(2026, 8, 10)):
    report = RecapBuilder().build(session_date=session)
    md = render_markdown(report)
    return write_recap(md, report.session_date, output_dir=str(tmp_path))


def test_drive_upload_uses_injected_service(tmp_path):
    from hy_recap.delivery_gdrive import upload_markdown_to_drive

    path = _write_sample_md(tmp_path)
    svc = _FakeDriveService()
    result = upload_markdown_to_drive(
        path,
        folder_id="folder-abc",
        share_with=["a@b.com"],
        service=svc,
        media_factory=lambda p: object(),
    )

    assert result.file_id == "fake-id-123"
    assert result.web_view_link.endswith("fake-id-123")
    assert svc.recorder["create"]["body"]["parents"] == ["folder-abc"]
    assert svc.recorder["create"]["body"]["name"] == "hy_recap_2026-08-10.md"
    assert svc.recorder["permissions"][0]["body"]["emailAddress"] == "a@b.com"


def test_drive_upload_as_google_doc_strips_extension(tmp_path):
    from hy_recap.delivery_gdrive import upload_markdown_to_drive

    path = _write_sample_md(tmp_path)
    svc = _FakeDriveService()
    upload_markdown_to_drive(
        path,
        folder_id="f",
        as_google_doc=True,
        service=svc,
        media_factory=lambda p: object(),
    )

    body = svc.recorder["create"]["body"]
    assert body["name"] == "hy_recap_2026-08-10"  # no .md
    assert body["mimeType"] == "application/vnd.google-apps.document"


def test_drive_upload_missing_file_raises(tmp_path):
    from hy_recap.delivery_gdrive import upload_markdown_to_drive

    with pytest.raises(FileNotFoundError):
        upload_markdown_to_drive(
            tmp_path / "nope.md", service=_FakeDriveService()
        )


def test_deliver_routes_drive_scheme(tmp_path, monkeypatch):
    import hy_recap.delivery as delivery

    path = _write_sample_md(tmp_path)
    calls = {}

    def fake_upload(p, folder_id=None, **kwargs):
        calls["path"] = p
        calls["folder_id"] = folder_id
        from hy_recap.delivery_gdrive import DriveUploadResult

        return DriveUploadResult(file_id="x", name="n", web_view_link="link")

    monkeypatch.setattr(
        "hy_recap.delivery_gdrive.upload_markdown_to_drive", fake_upload
    )
    delivery.deliver(path, "drive:my-folder")
    assert calls["folder_id"] == "my-folder"
    assert calls["path"] == path

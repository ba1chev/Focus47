import pytest

from tests.ui.conftest import ADMIN_ACCOUNT, ADMIN_PASSWORD

pytestmark = pytest.mark.ui


def _login(page, base_url, account=ADMIN_ACCOUNT, password=ADMIN_PASSWORD):
    page.goto(f"{base_url}/login")
    page.fill("#account", account)
    page.fill("#password", password)
    page.click("button[type=submit]")
    page.wait_for_url(f"{base_url}/")


def test_login_page_renders(page, live_server):
    page.goto(f"{live_server}/login")
    assert page.locator("#login-form").is_visible()
    assert page.locator("#account").is_visible()
    assert page.locator("#password").is_visible()


def test_unauthenticated_root_redirects_to_login(page, live_server):
    page.goto(f"{live_server}/")
    page.wait_for_url(f"{live_server}/login")


def test_login_flow_reaches_calendar(page, live_server):
    _login(page, live_server)
    assert page.locator("#new-btn").is_visible()
    assert page.locator(".calendar").is_visible()


def test_wrong_password_shows_error(page, live_server):
    page.goto(f"{live_server}/login")
    page.fill("#account", ADMIN_ACCOUNT)
    page.fill("#password", "definitely-wrong")
    page.click("button[type=submit]")
    error = page.locator("#error")
    error.wait_for(state="visible")
    assert error.inner_text().strip() != ""


def test_create_task_appears_in_calendar(page, live_server):
    _login(page, live_server)
    page.click("#new-btn")
    dialog = page.locator("#task-dialog")
    dialog.wait_for(state="visible")
    page.fill("#f-title", "UI Test Task")
    page.click("#save-btn")
    page.wait_for_selector(".task-block:has-text('UI Test Task')")
    assert page.locator(".task-block:has-text('UI Test Task')").count() >= 1


def test_logout_returns_to_login(page, live_server):
    _login(page, live_server)
    page.click("#logout-btn")
    page.wait_for_url(f"{live_server}/login")


def test_admin_sees_user_switch_dropdown(page, live_server):
    _login(page, live_server)
    page.wait_for_selector("#user-switch:not(.hidden)")
    assert page.locator("#user-switch").is_visible()

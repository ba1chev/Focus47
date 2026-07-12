import pytest
from playwright.sync_api import expect

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


def _create_task(page, title):
    page.click("#new-btn")
    page.locator("#task-dialog").wait_for(state="visible")
    page.fill("#f-title", title)
    page.click("#save-btn")
    page.wait_for_selector(f".task-block:has-text('{title}')")


def test_left_click_opens_read_only_view(page, live_server):
    _login(page, live_server)
    _create_task(page, "View Me")
    page.click(".task-block:has-text('View Me')")
    page.locator("#view-dialog").wait_for(state="visible")
    assert page.locator("#v-title").inner_text() == "View Me"
    assert not page.locator("#task-dialog").is_visible()


def test_description_url_becomes_a_link(page, live_server):
    _login(page, live_server)
    page.click("#new-btn")
    page.locator("#task-dialog").wait_for(state="visible")
    page.fill("#f-title", "Linky")
    page.fill("#f-description", "watch https://example.com/vid here")
    page.click("#save-btn")
    page.wait_for_selector(".task-block:has-text('Linky')")
    page.click(".task-block:has-text('Linky')")
    page.locator("#view-dialog").wait_for(state="visible")
    link = page.locator("#v-description a")
    expect(link).to_have_count(1)
    assert link.get_attribute("href") == "https://example.com/vid"
    assert link.get_attribute("target") == "_blank"


def test_right_click_shows_context_menu(page, live_server):
    _login(page, live_server)
    _create_task(page, "Menu Me")
    page.click(".task-block:has-text('Menu Me')", button="right")
    menu = page.locator("#ctx-menu")
    menu.wait_for(state="visible")
    assert menu.locator("button[data-act=edit]").is_visible()
    assert menu.locator("button[data-act=copy]").is_visible()
    assert menu.locator("button[data-act=delete]").is_visible()


def test_copy_creates_a_second_task(page, live_server):
    _login(page, live_server)
    _create_task(page, "Clone Me")
    assert page.locator(".task-block:has-text('Clone Me')").count() == 1
    page.click(".task-block:has-text('Clone Me')", button="right")
    page.locator("#ctx-menu").wait_for(state="visible")
    page.click("#ctx-menu button[data-act=copy]")
    expect(page.locator(".task-block:has-text('Clone Me')")).to_have_count(2)


def test_delete_removes_the_task(page, live_server):
    _login(page, live_server)
    _create_task(page, "Trash Me")
    page.on("dialog", lambda d: d.accept())
    page.click(".task-block:has-text('Trash Me')", button="right")
    page.locator("#ctx-menu").wait_for(state="visible")
    page.click("#ctx-menu button[data-act=delete]")
    expect(page.locator(".task-block:has-text('Trash Me')")).to_have_count(0)


def test_logout_returns_to_login(page, live_server):
    _login(page, live_server)
    page.click("#logout-btn")
    page.wait_for_url(f"{live_server}/login")


def test_admin_sees_user_switch_dropdown(page, live_server):
    _login(page, live_server)
    page.wait_for_selector("#user-switch:not(.hidden)")
    assert page.locator("#user-switch").is_visible()

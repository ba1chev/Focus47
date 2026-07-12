// ---- Config ----
const DAY_START_HOUR = 0;   // 12 AM
const DAY_END_HOUR = 23;    // 11 PM (last hour row)
const SLOT_HEIGHT = 56;     // must match --slot-height in CSS
const HOURS = [];
for (let h = DAY_START_HOUR; h <= DAY_END_HOUR; h++) HOURS.push(h);

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MINI_WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December"];

// ---- State ----
let currentWeekStart = mondayOf(new Date());
let miniMonth = new Date(currentWeekStart.getFullYear(), currentWeekStart.getMonth(), 1);
let tasks = [];
let editingId = null;
let me = null;               // current authenticated user
let viewUserId = null;       // dashboard being viewed (admin can switch)
let dayColumns = [];         // [{ el, date }] for the rendered week (used by drag)

// ---- DOM ----
const headerEl = document.getElementById("calendar-header");
const gutterEl = document.getElementById("time-gutter");
const daysEl = document.getElementById("days-container");
const bodyEl = document.getElementById("calendar-body");
const rangeEl = document.getElementById("week-range");
const dialog = document.getElementById("task-dialog");
const form = document.getElementById("task-form");
const miniLabelEl = document.getElementById("mini-month-label");
const miniWeekdaysEl = document.getElementById("mini-weekdays");
const miniGridEl = document.getElementById("mini-grid");
const userSwitchEl = document.getElementById("user-switch");
const newBtn = document.getElementById("new-btn");
const viewDialog = document.getElementById("view-dialog");
const ctxMenu = document.getElementById("ctx-menu");

// True when viewing your own dashboard (editing allowed).
function isOwnBoard() {
    return !me || viewUserId === null || viewUserId === me.id;
}

// Reads the double-submit CSRF token the server set as a readable cookie.
function csrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
}

// fetch wrapper that attaches the CSRF header on mutating requests.
function apiFetch(url, options = {}) {
    const method = (options.method || "GET").toUpperCase();
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        options.headers = { ...(options.headers || {}), "X-CSRF-Token": csrfToken() };
    }
    return fetch(url, options);
}

// ---- Date helpers ----
function mondayOf(date) {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    const day = d.getDay();               // 0=Sun..6=Sat
    const diff = (day === 0 ? -6 : 1 - day);
    d.setDate(d.getDate() + diff);
    return d;
}
function addDays(date, n) {
    const d = new Date(date);
    d.setDate(d.getDate() + n);
    return d;
}
function sameDay(a, b) {
    return a.getFullYear() === b.getFullYear() &&
        a.getMonth() === b.getMonth() &&
        a.getDate() === b.getDate();
}
// Local ISO without timezone conversion (for datetime-local + API)
function toLocalISO(date) {
    const pad = (n) => String(n).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
        `T${pad(date.getHours())}:${pad(date.getMinutes())}:00`;
}
function parseISO(s) {
    // Treat stored ISO as local time
    return new Date(s);
}
function fmtHour(h) {
    const period = h < 12 ? "AM" : "PM";
    let hr = h % 12;
    if (hr === 0) hr = 12;
    return `${hr} ${period}`;
}

// ---- Rendering ----
function dayCount() { return 7; }

function renderHeader(weekStart) {
    const n = dayCount();
    headerEl.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
    daysEl.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
    headerEl.innerHTML = "";
    const today = new Date();
    for (let i = 0; i < n; i++) {
        const d = addDays(weekStart, i);
        const cell = document.createElement("div");
        cell.className = "day-header" + (sameDay(d, today) ? " today" : "");
        cell.innerHTML = `<div class="day-num">${d.getDate()}</div>` +
            `<div>${WEEKDAYS[d.getDay()]}</div>`;
        headerEl.appendChild(cell);
    }
    // week range label
    const last = addDays(weekStart, n - 1);
    const rangeText = weekStart.getMonth() === last.getMonth()
        ? `${MONTHS[weekStart.getMonth()]} ${weekStart.getDate()}–${last.getDate()}, ${last.getFullYear()}`
        : `${MONTHS[weekStart.getMonth()]} ${weekStart.getDate()} – ${MONTHS[last.getMonth()]} ${last.getDate()}, ${last.getFullYear()}`;
    rangeEl.textContent = rangeText;
}

function renderGutter() {
    gutterEl.innerHTML = "";
    for (const h of HOURS) {
        const label = document.createElement("div");
        label.className = "time-label";
        label.textContent = fmtHour(h);
        gutterEl.appendChild(label);
    }
}

function renderMiniWeekdays() {
    miniWeekdaysEl.innerHTML = "";
    for (const w of MINI_WEEKDAYS) {
        const cell = document.createElement("div");
        cell.className = "mini-weekday";
        cell.textContent = w;
        miniWeekdaysEl.appendChild(cell);
    }
}

function renderMiniCal() {
    miniLabelEl.textContent = `${MONTHS[miniMonth.getMonth()]} ${miniMonth.getFullYear()}`;
    miniGridEl.innerHTML = "";
    const today = new Date();
    const weekEnd = addDays(currentWeekStart, 6);
    // first cell = Sunday on/before the 1st
    const gridStart = addDays(miniMonth, -miniMonth.getDay());
    for (let i = 0; i < 42; i++) {
        const d = addDays(gridStart, i);
        const cell = document.createElement("div");
        cell.className = "mini-day";
        if (d.getMonth() !== miniMonth.getMonth()) cell.classList.add("other-month");
        if (sameDay(d, today)) cell.classList.add("today");
        if (d >= currentWeekStart && d <= weekEnd) cell.classList.add("in-week");
        cell.textContent = d.getDate();
        cell.addEventListener("click", () => {
            currentWeekStart = mondayOf(d);
            render();
        });
        miniGridEl.appendChild(cell);
    }
}

function renderDays(weekStart) {
    const n = dayCount();
    const editable = isOwnBoard();
    daysEl.innerHTML = "";
    dayColumns = [];
    for (let i = 0; i < n; i++) {
        const col = document.createElement("div");
        col.className = "day-column";
        const dayDate = addDays(weekStart, i);
        // background hour cells (click to create)
        for (const h of HOURS) {
            const cell = document.createElement("div");
            cell.className = "hour-cell";
            if (editable) cell.addEventListener("click", () => openCreate(dayDate, h));
            col.appendChild(cell);
        }
        daysEl.appendChild(col);
        dayColumns.push({ col, dayDate });
    }
    // place task blocks, grouped per day so overlaps sit side by side
    for (let i = 0; i < n; i++) {
        const dayTasks = tasks
            .filter((t) => sameDay(parseISO(t.start), dayColumns[i].dayDate))
            .sort((a, b) => parseISO(a.start) - parseISO(b.start));
        for (const layout of layoutDay(dayTasks)) {
            placeTask(dayColumns[i].col, layout.task, layout.start, layout.end,
                editable, layout.left, layout.width);
        }
    }
}

// Assign overlapping tasks to lanes so they render side by side.
// Returns [{ task, start, end, left, width }] with left/width as 0..1 fractions.
function layoutDay(dayTasks) {
    const items = dayTasks.map((t) => ({
        task: t, start: parseISO(t.start), end: parseISO(t.end),
    }));
    const result = [];
    let cluster = [];
    let clusterEnd = null;

    const flush = () => {
        if (!cluster.length) return;
        const lanes = []; // lanes[j] = end time of last task in lane j
        for (const it of cluster) {
            let lane = lanes.findIndex((endTime) => it.start >= endTime);
            if (lane === -1) { lane = lanes.length; lanes.push(it.end); }
            else lanes[lane] = it.end;
            it.lane = lane;
        }
        const laneCount = lanes.length;
        for (const it of cluster) {
            result.push({
                task: it.task, start: it.start, end: it.end,
                left: it.lane / laneCount, width: 1 / laneCount,
            });
        }
        cluster = [];
        clusterEnd = null;
    };

    for (const it of items) {
        if (clusterEnd !== null && it.start >= clusterEnd) flush();
        cluster.push(it);
        clusterEnd = clusterEnd === null ? it.end : new Date(Math.max(clusterEnd, it.end));
    }
    flush();
    return result;
}

function placeTask(col, task, start, end, editable, left, width) {
    const startMin = (start.getHours() - DAY_START_HOUR) * 60 + start.getMinutes();
    const durMin = Math.max((end - start) / 60000, 15); // keep a clickable minimum
    const top = (startMin / 60) * SLOT_HEIGHT;
    const height = (durMin / 60) * SLOT_HEIGHT;

    const block = document.createElement("div");
    block.className = `task-block prio-${task.priority} status-${task.status}`;
    if (height < 34) block.classList.add("compact");
    block.style.top = `${Math.max(top, 0)}px`;
    block.style.height = `${height - 2}px`;
    // lane geometry: gap on both sides, split remaining width across lanes
    const gap = 3;
    block.style.left = `calc(${left * 100}% + ${gap}px)`;
    block.style.width = `calc(${width * 100}% - ${gap * 2}px)`;

    const timeStr = `${fmtHour(start.getHours()).replace(" ", "")}`;
    block.innerHTML =
        `<div class="task-title">${escapeHtml(task.title)}</div>` +
        `<div class="task-meta">${timeStr}${task.category ? " · " + escapeHtml(task.category) : ""}</div>`;
    // left click always previews (read-only), even on your own board
    block.addEventListener("click", (e) => {
        e.stopPropagation();
        if (block._suppressClick) { block._suppressClick = false; return; }
        openView(task);
    });
    if (editable) {
        block.classList.add("draggable");
        block.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            showContextMenu(e.clientX, e.clientY, task);
        });
        attachDrag(block, task, start, end);
    } else {
        block.style.cursor = "default";
    }
    col.appendChild(block);
}

function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s ?? "";
    return div.innerHTML;
}

// ---- Read-only preview ----
const STATUS_LABELS = { todo: "To do", in_progress: "In progress", done: "Done" };

function fmtTimeRange(start, end) {
    const t = (d) => {
        const h = fmtHour(d.getHours()).replace(" ", "");
        const m = d.getMinutes();
        return m ? h.replace(/(AM|PM)/, `:${String(m).padStart(2, "0")} $1`) : h;
    };
    return `${t(start)} – ${t(end)}`;
}

function openView(task) {
    const start = parseISO(task.start);
    const end = parseISO(task.end);
    document.getElementById("v-title").textContent = task.title;
    document.getElementById("v-time").textContent = fmtTimeRange(start, end);
    const bits = [STATUS_LABELS[task.status] || task.status,
        `${task.priority} priority`];
    if (task.category) bits.push(task.category);
    document.getElementById("v-meta").textContent = bits.join(" · ");
    const desc = document.getElementById("v-description");
    desc.textContent = task.description || "";
    desc.classList.toggle("hidden", !task.description);
    const editBtn = document.getElementById("v-edit-btn");
    editBtn.classList.toggle("hidden", !isOwnBoard());
    editBtn.onclick = () => { viewDialog.close(); openEdit(task); };
    viewDialog.showModal();
}

// ---- Context menu ----
let ctxTask = null;

function showContextMenu(x, y, task) {
    ctxTask = task;
    ctxMenu.style.left = `${x}px`;
    ctxMenu.style.top = `${y}px`;
    ctxMenu.classList.remove("hidden");
}

function hideContextMenu() {
    ctxMenu.classList.add("hidden");
    ctxTask = null;
}

async function copyTask(task) {
    const payload = {
        title: task.title, description: task.description,
        start: task.start, end: task.end,
        status: task.status, priority: task.priority,
        category: task.category, repeat_weeks: 0,
    };
    await apiFetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    await loadTasks();
}

// ---- Drag & drop (move) ----
function snapMinutes(min) { return Math.round(min / 30) * 30; }

function attachDrag(block, task, start, end) {
    const durationMs = end - start;
    block.addEventListener("mousedown", (e) => {
        if (e.button !== 0) return; // left button only
        const startX = e.clientX;
        const startY = e.clientY;
        let dragging = false;

        const onMove = (ev) => {
            if (!dragging &&
                Math.abs(ev.clientX - startX) + Math.abs(ev.clientY - startY) < 4) {
                return;
            }
            dragging = true;
            block.classList.add("dragging");
        };

        const onUp = async (ev) => {
            document.removeEventListener("mousemove", onMove);
            document.removeEventListener("mouseup", onUp);
            if (!dragging) return;
            block.classList.remove("dragging");
            block._suppressClick = true; // swallow the click that follows a drag
            const dropped = dropTarget(ev.clientX, ev.clientY);
            if (dropped) {
                const newStart = dropped;
                const newEnd = new Date(newStart.getTime() + durationMs);
                await apiFetch(`/api/tasks/${task.id}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        start: toLocalISO(newStart), end: toLocalISO(newEnd),
                    }),
                });
                await loadTasks();
            }
        };

        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
    });
}

// Resolve a drop point to a snapped start Date, or null if outside the grid.
function dropTarget(clientX, clientY) {
    let hit = null;
    for (const { col, dayDate } of dayColumns) {
        const r = col.getBoundingClientRect();
        if (clientX >= r.left && clientX < r.right) {
            const offsetY = clientY - r.top;
            const rawMin = (offsetY / SLOT_HEIGHT) * 60 + DAY_START_HOUR * 60;
            const min = Math.max(0, Math.min(snapMinutes(rawMin), 23 * 60 + 30));
            const d = new Date(dayDate);
            d.setHours(0, 0, 0, 0);
            d.setMinutes(min);
            hit = d;
            break;
        }
    }
    return hit;
}

// ---- Data ----
async function loadTasks() {
    const start = toLocalISO(currentWeekStart);
    const end = toLocalISO(addDays(currentWeekStart, 7));
    let url = `/api/tasks?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
    if (me && viewUserId !== null && viewUserId !== me.id) {
        url += `&user_id=${viewUserId}`;
    }
    const res = await fetch(url);
    tasks = await res.json();
    newBtn.classList.toggle("hidden", !isOwnBoard());
    renderDays(currentWeekStart);
}

async function render() {
    miniMonth = new Date(currentWeekStart.getFullYear(), currentWeekStart.getMonth(), 1);
    renderMiniCal();
    renderGutter();
    renderHeader(currentWeekStart);
    await loadTasks();
}

// ---- Dialog ----
function setFormValues(v) {
    document.getElementById("f-title").value = v.title || "";
    document.getElementById("f-description").value = v.description || "";
    document.getElementById("f-start").value = (v.start || "").slice(0, 16);
    document.getElementById("f-end").value = (v.end || "").slice(0, 16);
    document.getElementById("f-status").value = v.status || "todo";
    document.getElementById("f-priority").value = v.priority || "medium";
    document.getElementById("f-category").value = v.category || "";
    document.getElementById("f-repeat").value = 0;
}

function openCreate(dayDate, hour) {
    editingId = null;
    document.getElementById("dialog-title").textContent = "New task";
    document.getElementById("delete-btn").classList.add("hidden");
    const start = new Date(dayDate);
    start.setHours(hour, 0, 0, 0);
    const end = new Date(start);
    end.setHours(hour + 1);
    setFormValues({ start: toLocalISO(start), end: toLocalISO(end) });
    dialog.showModal();
}

function openEdit(task) {
    editingId = task.id;
    document.getElementById("dialog-title").textContent = "Edit task";
    document.getElementById("delete-btn").classList.remove("hidden");
    setFormValues(task);
    dialog.showModal();
}

function collectForm() {
    return {
        title: document.getElementById("f-title").value.trim(),
        description: document.getElementById("f-description").value,
        start: document.getElementById("f-start").value + ":00",
        end: document.getElementById("f-end").value + ":00",
        status: document.getElementById("f-status").value,
        priority: document.getElementById("f-priority").value,
        category: document.getElementById("f-category").value,
        repeat_weeks: Number(document.getElementById("f-repeat").value) || 0,
    };
}

// ---- Events ----
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = collectForm();
    if (!payload.title) return;
    if (editingId === null) {
        await apiFetch("/api/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    } else {
        await apiFetch(`/api/tasks/${editingId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    }
    dialog.close();
    await loadTasks();
});

document.getElementById("cancel-btn").addEventListener("click", () => dialog.close());

document.getElementById("v-close-btn").addEventListener("click", () => viewDialog.close());

ctxMenu.addEventListener("click", (e) => {
    const act = e.target.dataset.act;
    if (!act || !ctxTask) return;
    const task = ctxTask;
    hideContextMenu();
    if (act === "edit") openEdit(task);
    else if (act === "copy") copyTask(task);
});
document.addEventListener("click", (e) => {
    if (!ctxMenu.classList.contains("hidden") && !ctxMenu.contains(e.target)) {
        hideContextMenu();
    }
});
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") hideContextMenu();
});
window.addEventListener("scroll", hideContextMenu, true);

document.getElementById("delete-btn").addEventListener("click", async () => {
    if (editingId === null) return;
    if (!confirm("Delete this task?")) return;
    await apiFetch(`/api/tasks/${editingId}`, { method: "DELETE" });
    dialog.close();
    await loadTasks();
});

document.getElementById("new-btn").addEventListener("click", () => {
    const d = new Date(currentWeekStart);
    openCreate(d, 9);
});

document.getElementById("today-btn").addEventListener("click", () => {
    currentWeekStart = mondayOf(new Date());
    render();
});
document.getElementById("prev-btn").addEventListener("click", () => {
    currentWeekStart = addDays(currentWeekStart, -7);
    render();
});
document.getElementById("next-btn").addEventListener("click", () => {
    currentWeekStart = addDays(currentWeekStart, 7);
    render();
});

document.getElementById("logout-btn").addEventListener("click", async () => {
    await apiFetch("/api/auth/logout", { method: "POST" });
    window.location = "/login";
});

document.getElementById("mini-prev").addEventListener("click", () => {
    miniMonth.setMonth(miniMonth.getMonth() - 1);
    renderMiniCal();
});
document.getElementById("mini-next").addEventListener("click", () => {
    miniMonth.setMonth(miniMonth.getMonth() + 1);
    renderMiniCal();
});

userSwitchEl.addEventListener("change", () => {
    viewUserId = Number(userSwitchEl.value);
    render();
});

async function initUser() {
    const res = await fetch("/api/auth/me");
    if (!res.ok) return;
    me = await res.json();
    viewUserId = me.id;
    if (me.role === "admin") {
        const users = await (await fetch("/api/users")).json();
        userSwitchEl.innerHTML = "";
        for (const u of users) {
            const opt = document.createElement("option");
            opt.value = u.id;
            opt.textContent = u.id === me.id ? `${u.name} (you)` : u.name;
            userSwitchEl.appendChild(opt);
        }
        userSwitchEl.value = String(me.id);
        userSwitchEl.classList.remove("hidden");
    }
}

renderMiniWeekdays();
initUser().then(render);

// Start scrolled to the morning (7 AM), like Teams.
bodyEl.scrollTop = (7 - DAY_START_HOUR) * SLOT_HEIGHT;

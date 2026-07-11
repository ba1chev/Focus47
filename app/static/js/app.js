// ---- Config ----
const DAY_START_HOUR = 0;   // 12 AM
const DAY_END_HOUR = 23;    // 11 PM (last hour row)
const SLOT_HEIGHT = 56;     // must match --slot-height in CSS
const HOURS = [];
for (let h = DAY_START_HOUR; h <= DAY_END_HOUR; h++) HOURS.push(h);

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December"];

// ---- State ----
let currentWeekStart = mondayOf(new Date());
let workWeek = true;         // Mon–Fri vs full week
let tasks = [];
let editingId = null;

// ---- DOM ----
const headerEl = document.getElementById("calendar-header");
const gutterEl = document.getElementById("time-gutter");
const daysEl = document.getElementById("days-container");
const bodyEl = document.getElementById("calendar-body");
const rangeEl = document.getElementById("week-range");
const dialog = document.getElementById("task-dialog");
const form = document.getElementById("task-form");

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
function dayCount() { return workWeek ? 5 : 7; }

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

function renderDays(weekStart) {
    const n = dayCount();
    daysEl.innerHTML = "";
    const columns = [];
    for (let i = 0; i < n; i++) {
        const col = document.createElement("div");
        col.className = "day-column";
        const dayDate = addDays(weekStart, i);
        // background hour cells (click to create)
        for (const h of HOURS) {
            const cell = document.createElement("div");
            cell.className = "hour-cell";
            cell.addEventListener("click", () => openCreate(dayDate, h));
            col.appendChild(cell);
        }
        daysEl.appendChild(col);
        columns.push({ col, dayDate });
    }
    // place task blocks
    for (const t of tasks) {
        const start = parseISO(t.start);
        const end = parseISO(t.end);
        for (let i = 0; i < n; i++) {
            if (sameDay(start, columns[i].dayDate)) {
                placeTask(columns[i].col, t, start, end);
                break;
            }
        }
    }
}

function placeTask(col, task, start, end) {
    const startMin = (start.getHours() - DAY_START_HOUR) * 60 + start.getMinutes();
    let durMin = (end - start) / 60000;
    if (durMin < 30) durMin = 30; // minimum visible height
    const top = (startMin / 60) * SLOT_HEIGHT;
    const height = (durMin / 60) * SLOT_HEIGHT;

    const block = document.createElement("div");
    block.className = `task-block prio-${task.priority}` +
        (task.status === "done" ? " done" : "");
    block.style.top = `${Math.max(top, 0)}px`;
    block.style.height = `${height - 2}px`;
    block.style.background = task.color || "#6264a7";

    const timeStr = `${fmtHour(start.getHours()).replace(" ", "")}`;
    block.innerHTML =
        `<div class="task-title">${escapeHtml(task.title)}</div>` +
        `<div class="task-meta">${timeStr}${task.category ? " · " + escapeHtml(task.category) : ""}</div>`;
    block.addEventListener("click", (e) => {
        e.stopPropagation();
        openEdit(task);
    });
    col.appendChild(block);
}

function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s ?? "";
    return div.innerHTML;
}

// ---- Data ----
async function loadTasks() {
    const start = toLocalISO(currentWeekStart);
    const end = toLocalISO(addDays(currentWeekStart, 7));
    const res = await fetch(`/api/tasks?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
    tasks = await res.json();
    renderDays(currentWeekStart);
}

async function render() {
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
    document.getElementById("f-color").value = v.color || "#6264a7";
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
        color: document.getElementById("f-color").value,
    };
}

// ---- Events ----
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = collectForm();
    if (!payload.title) return;
    if (editingId === null) {
        await fetch("/api/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    } else {
        await fetch(`/api/tasks/${editingId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    }
    dialog.close();
    await loadTasks();
});

document.getElementById("cancel-btn").addEventListener("click", () => dialog.close());

document.getElementById("delete-btn").addEventListener("click", async () => {
    if (editingId === null) return;
    if (!confirm("Delete this task?")) return;
    await fetch(`/api/tasks/${editingId}`, { method: "DELETE" });
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
document.getElementById("view-toggle").addEventListener("click", (e) => {
    workWeek = !workWeek;
    e.target.textContent = workWeek ? "Work week" : "Full week";
    render();
});

render();

// Start scrolled to the morning (7 AM), like Teams.
bodyEl.scrollTop = (7 - DAY_START_HOUR) * SLOT_HEIGHT;

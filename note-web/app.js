const API_URL = "http://127.0.0.1:8000/notes";

const notesList = document.getElementById("notes-list");
const noteEditor = document.getElementById("note-editor");
const noteTitle = document.getElementById("note-title");
const noteContent = document.getElementById("note-content");
const noteUrl = document.getElementById("note-url");
const newNoteBtn = document.getElementById("new-note-btn");
const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");
const searchInput = document.getElementById("search-input");

let editingId = null;
let allNotes = [];

async function fetchNotes() {
    const res = await fetch(API_URL);
    allNotes = await res.json();
    renderNotes(allNotes);
}

function renderNotes(notes) {
    if (notes.length === 0) {
        notesList.innerHTML = '<div class="empty-state">No notes yet. Create one!</div>';
        return;
    }

    notesList.innerHTML = notes.map(note => `
        <div class="note-card" data-id="${note.id}">
            <div class="note-card-title">${note.title}</div>
            <div class="note-card-content">${note.content || ""}</div>
            <div class="note-card-meta">${formatDate(note.created_at)}</div>
        </div>
    `).join("");

    notesList.querySelectorAll(".note-card").forEach(card => {
        card.addEventListener("click", () => {
            const id = parseInt(card.dataset.id);
            const note = allNotes.find(n => n.id === id);
            if (note) {
                openEditor(note.id, note.title, note.content);
            }
        });
    });
}

function openEditor(id, title, content) {
    editingId = id;
    noteTitle.value = title;
    noteContent.value = content;
    noteEditor.classList.remove("hidden");
    notesList.classList.add("hidden");
    saveBtn.textContent = "Save";
    noteTitle.focus();
}

function openNewNote() {
    editingId = null;
    noteTitle.value = "";
    noteContent.value = "";
    noteUrl.value = "";
    noteEditor.classList.remove("hidden");
    notesList.classList.add("hidden");
    saveBtn.textContent = "Create";
    noteTitle.focus();
}

async function fetchFromUrl(url) {
    try {
        const res = await fetch(`${API_URL}/fetch-url`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });
        const data = await res.json();
        noteContent.value = data.content;
    } catch (err) {
        noteContent.value = "";
    }
}

function closeEditor() {
    noteEditor.classList.add("hidden");
    notesList.classList.remove("hidden");
    fetchNotes();
}

async function saveNote() {
    const title = noteTitle.value.trim();
    const content = noteContent.value.trim();

    if (!title) {
        noteTitle.focus();
        return;
    }

    const payload = { title, content };

    if (editingId) {
        await fetch(`${API_URL}/${editingId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    } else {
        await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    }

    closeEditor();
}

async function deleteNote(id) {
    await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    closeEditor();
}

function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
}

function filterNotes(query) {
    if (!query) {
        renderNotes(allNotes);
        return;
    }
    const filtered = allNotes.filter(note =>
        note.title.toLowerCase().includes(query.toLowerCase()) ||
        (note.content && note.content.toLowerCase().includes(query.toLowerCase()))
    );
    const highlighted = filtered.map(note => ({
        ...note,
        title: highlightText(note.title, query),
        content: note.content ? highlightText(note.content, query) : "",
    }));
    renderNotes(highlighted);
}

function formatDate(dateStr) {
    const d = new Date(dateStr + "Z");
    return d.toLocaleDateString(undefined, {
        year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
}

newNoteBtn.addEventListener("click", openNewNote);
cancelBtn.addEventListener("click", closeEditor);
saveBtn.addEventListener("click", saveNote);

searchInput.addEventListener("input", (e) => {
    filterNotes(e.target.value);
});

noteUrl.addEventListener("blur", async () => {
    const url = noteUrl.value.trim();
    if (url) {
        await fetchFromUrl(url);
    }
});

noteTitle.addEventListener("keydown", (e) => {
    if (e.key === "Enter") noteContent.focus();
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !noteEditor.classList.contains("hidden")) {
        closeEditor();
    }
});

fetchNotes();

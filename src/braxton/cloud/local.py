from flask import Flask, request, jsonify, send_file, render_template_string
from pathlib import Path
import socket
import shutil
from datetime import datetime

app = Flask(__name__)

# ============================================================
# CONFIG
# ============================================================

HOST = "0.0.0.0"

BASE_DIR = Path(__file__).resolve().parent
SHARE_DIR = BASE_DIR / "HomeCloud"

SHARE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SECURITY / PATH HANDLING
# ============================================================

def safe_path(relative_path: str = "") -> Path:
    """
    Converts a relative cloud path into an absolute path while
    preventing access outside SHARE_DIR.
    """

    relative_path = str(relative_path or "")
    relative_path = relative_path.replace("\\", "/").strip("/")

    target = (SHARE_DIR / relative_path).resolve()
    base = SHARE_DIR.resolve()

    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError("Invalid path")

    return target


def get_local_ip():
    """
    Try to determine the local LAN IPv4 address.
    """

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:

        try:
            return socket.gethostbyname(
                socket.gethostname()
            )

        except Exception:

            return "127.0.0.1"


# ============================================================
# HTML
# ============================================================

HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>HomeCloud</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    background: #0a0a0a;

    color: #ffffff;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.container {

    max-width: 1100px;

    margin: auto;

    padding: 30px 20px 60px;
}


/* ============================================================
   HEADER
   ============================================================ */

.header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 30px;
}

.logo {

    display: flex;

    align-items: center;

    gap: 12px;
}

.logo-icon {

    width: 42px;

    height: 42px;

    border-radius: 12px;

    background: #00c853;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #000;

    font-weight: 900;

    font-size: 20px;
}

.logo h1 {

    margin: 0;

    font-size: 22px;
}

.logo span {

    color: #777;

    font-size: 13px;
}


/* ============================================================
   STATUS
   ============================================================ */

.status {

    display: flex;

    align-items: center;

    gap: 8px;

    color: #aaa;

    font-size: 13px;
}

.status-dot {

    width: 9px;

    height: 9px;

    border-radius: 50%;

    background: #00c853;

    box-shadow: 0 0 10px #00c853;
}


/* ============================================================
   UPLOAD AREA
   ============================================================ */

.upload-area {

    border: 2px dashed #303030;

    background: #111111;

    border-radius: 18px;

    padding: 45px 20px;

    text-align: center;

    transition: 0.2s;

    cursor: pointer;
}

.upload-area:hover,
.upload-area.dragover {

    border-color: #00c853;

    background: #0d170f;
}

.upload-icon {

    font-size: 42px;

    margin-bottom: 12px;
}

.upload-area h2 {

    margin: 0 0 8px;

    font-size: 20px;
}

.upload-area p {

    margin: 0;

    color: #777;
}

.upload-buttons {

    display: flex;

    justify-content: center;

    gap: 10px;

    flex-wrap: wrap;

    margin-top: 20px;
}

.upload-button {

    display: inline-block;

    padding: 11px 20px;

    background: #00c853;

    color: #000;

    border-radius: 10px;

    font-weight: 700;

    cursor: pointer;
}

.upload-button.secondary {

    background: #1d1d1d;

    color: white;

    border: 1px solid #303030;
}

.upload-button:hover {

    opacity: 0.9;
}


/* ============================================================
   TOOLBAR
   ============================================================ */

.toolbar {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin: 30px 0 15px;

    gap: 15px;
}

.path {

    color: #888;

    font-size: 14px;

    overflow: hidden;

    text-overflow: ellipsis;
}

.actions {

    display: flex;

    gap: 10px;
}

button {

    border: 0;

    cursor: pointer;

    font-family: inherit;
}

.button {

    padding: 10px 15px;

    border-radius: 9px;

    background: #1a1a1a;

    color: white;
}

.button:hover {

    background: #252525;
}

.button.green {

    background: #00c853;

    color: black;

    font-weight: 700;
}


/* ============================================================
   SEARCH
   ============================================================ */

.search {

    margin-bottom: 15px;
}

.search input {

    width: 100%;

    background: #111;

    border: 1px solid #242424;

    color: white;

    padding: 13px 15px;

    border-radius: 10px;

    outline: none;
}

.search input:focus {

    border-color: #00c853;
}


/* ============================================================
   FILE LIST
   ============================================================ */

.files {

    background: #111;

    border-radius: 15px;

    overflow: hidden;

    border: 1px solid #1c1c1c;
}

.file {

    display: grid;

    grid-template-columns:
        1fr
        130px
        160px
        130px;

    align-items: center;

    gap: 10px;

    padding: 15px 18px;

    border-bottom: 1px solid #1e1e1e;
}

.file:last-child {

    border-bottom: none;
}

.file:hover {

    background: #151515;
}

.file-name {

    display: flex;

    align-items: center;

    gap: 12px;

    min-width: 0;
}

.file-icon {

    font-size: 23px;
}

.file-name-text {

    overflow: hidden;

    text-overflow: ellipsis;

    white-space: nowrap;
}

.file-info {

    color: #777;

    font-size: 13px;
}

.file-actions {

    display: flex;

    justify-content: flex-end;

    gap: 7px;
}

.file-actions a,
.file-actions button {

    background: #1b1b1b;

    color: white;

    padding: 7px 10px;

    border-radius: 7px;

    text-decoration: none;
}

.file-actions a:hover,
.file-actions button:hover {

    background: #292929;
}

.delete:hover {

    background: #451414 !important;
}


/* ============================================================
   PROGRESS
   ============================================================ */

.progress-container {

    display: none;

    margin-top: 20px;

    background: #111;

    border: 1px solid #222;

    border-radius: 12px;

    padding: 15px;
}

.progress-container.active {

    display: block;
}

.progress-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;
}

.progress-text {

    color: #aaa;

    font-size: 13px;

    overflow: hidden;

    text-overflow: ellipsis;

    white-space: nowrap;
}

.progress-percent {

    color: #00c853;

    font-weight: 700;

    font-size: 14px;
}

.progress-bar-background {

    height: 8px;

    background: #222;

    border-radius: 10px;

    overflow: hidden;

    margin-top: 10px;
}

.progress-bar {

    height: 100%;

    width: 0%;

    background: #00c853;

    transition: width 0.1s;
}

.progress-details {

    margin-top: 8px;

    color: #666;

    font-size: 12px;
}


/* ============================================================
   EMPTY
   ============================================================ */

.empty {

    text-align: center;

    padding: 60px 20px;

    color: #666;
}

.empty-icon {

    font-size: 40px;

    margin-bottom: 10px;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 750px) {

    .container {

        padding: 20px 12px 40px;
    }

    .header {

        align-items: flex-start;
    }

    .file {

        grid-template-columns:
            1fr
            auto;
    }

    .file-info {

        display: none;
    }

    .file-actions {

        grid-column: 2;

        grid-row: 1;
    }

    .upload-area {

        padding: 35px 15px;
    }

    .toolbar {

        flex-direction: column;

        align-items: stretch;
    }

    .actions {

        width: 100%;
    }

    .actions button {

        flex: 1;
    }
}

</style>

</head>


<body>


<div class="container">


    <!-- ======================================================
         HEADER
         ====================================================== -->

    <div class="header">

        <div class="logo">

            <div class="logo-icon">
                ☁
            </div>

            <div>

                <h1>HomeCloud</h1>

                <span>
                    Private local file sharing
                </span>

            </div>

        </div>


        <div class="status">

            <div class="status-dot"></div>

            Online

        </div>

    </div>


    <!-- ======================================================
         UPLOAD
         ====================================================== -->

    <div
        class="upload-area"
        id="dropArea"
    >

        <div class="upload-icon">
            ⬆
        </div>

        <h2>
            Drop files or folders here
        </h2>

        <p>
            Upload files and complete folder structures
        </p>


        <div class="upload-buttons">


            <!-- FILE PICKER -->

            <label class="upload-button">

                Choose files

                <input
                    id="fileInput"
                    type="file"
                    multiple
                    hidden
                >

            </label>


            <!-- FOLDER PICKER -->

            <label class="upload-button secondary">

                Choose folder

                <input
                    id="folderInput"
                    type="file"
                    webkitdirectory
                    directory
                    multiple
                    hidden
                >

            </label>


        </div>

    </div>


    <!-- ======================================================
         PROGRESS
         ====================================================== -->

    <div
        class="progress-container"
        id="progressContainer"
    >

        <div class="progress-header">

            <div
                class="progress-text"
                id="progressText"
            >
                Preparing upload...
            </div>

            <div
                class="progress-percent"
                id="progressPercent"
            >
                0%
            </div>

        </div>


        <div class="progress-bar-background">

            <div
                class="progress-bar"
                id="progressBar"
            ></div>

        </div>


        <div
            class="progress-details"
            id="progressDetails"
        >
            0 B / 0 B
        </div>

    </div>


    <!-- ======================================================
         TOOLBAR
         ====================================================== -->

    <div class="toolbar">


        <div class="path">

            📁 /{{ current_path }}

        </div>


        <div class="actions">


            {% if current_path %}

            <button
                class="button"
                onclick="goUp()"
            >
                ← Back
            </button>

            {% endif %}


            <button
                class="button green"
                onclick="createFolder()"
            >
                + New folder
            </button>


        </div>

    </div>


    <!-- ======================================================
         SEARCH
         ====================================================== -->

    <div class="search">

        <input
            id="search"
            type="text"
            placeholder="Search files..."
            oninput="searchFiles()"
        >

    </div>


    <!-- ======================================================
         FILES
         ====================================================== -->

    <div
        class="files"
        id="fileList"
    >

        {% if items %}


            {% for item in items %}


                {% if item.is_dir %}


                <div
                    class="file"
                    data-name="{{ item.name|lower }}"
                >

                    <div class="file-name">

                        <div class="file-icon">
                            📁
                        </div>

                        <div class="file-name-text">

                            <a
                                href="/?path={{ item.path|urlencode }}"
                                style="
                                    color:white;
                                    text-decoration:none
                                "
                            >
                                {{ item.name }}
                            </a>

                        </div>

                    </div>


                    <div class="file-info">
                        Folder
                    </div>


                    <div class="file-info">
                        —
                    </div>


                    <div class="file-actions">

                        <button
                            class="delete"
                            onclick='deleteItem(
                                {{ item.path|tojson }}
                            )'
                        >
                            Delete
                        </button>

                    </div>

                </div>


                {% else %}


                <div
                    class="file"
                    data-name="{{ item.name|lower }}"
                >

                    <div class="file-name">

                        <div class="file-icon">
                            {{ item.icon }}
                        </div>

                        <div class="file-name-text">
                            {{ item.name }}
                        </div>

                    </div>


                    <div class="file-info">
                        {{ item.size }}
                    </div>


                    <div class="file-info">
                        {{ item.modified }}
                    </div>


                    <div class="file-actions">

                        <a
                            href="/download?path={{ item.path|urlencode }}"
                        >
                            Download
                        </a>


                        <button
                            class="delete"
                            onclick='deleteItem(
                                {{ item.path|tojson }}
                            )'
                        >
                            Delete
                        </button>

                    </div>

                </div>


                {% endif %}


            {% endfor %}


        {% else %}


            <div class="empty">

                <div class="empty-icon">
                    📂
                </div>

                <div>
                    This folder is empty
                </div>

            </div>


        {% endif %}

    </div>

</div>


<script>

/* ============================================================
   ELEMENTS
   ============================================================ */

const dropArea = document.getElementById("dropArea");
const fileInput = document.getElementById("fileInput");
const folderInput = document.getElementById("folderInput");

const progressContainer =
    document.getElementById("progressContainer");

const progressBar =
    document.getElementById("progressBar");

const progressText =
    document.getElementById("progressText");

const progressPercent =
    document.getElementById("progressPercent");

const progressDetails =
    document.getElementById("progressDetails");


/* ============================================================
   CURRENT CLOUD PATH
   ============================================================ */

const currentCloudPath =
    {{ current_path|tojson }};


/* ============================================================
   DRAG & DROP VISUALS
   ============================================================ */

dropArea.addEventListener("dragover", function(event) {

    event.preventDefault();

    event.dataTransfer.dropEffect = "copy";

    dropArea.classList.add("dragover");

});


dropArea.addEventListener("dragleave", function(event) {

    if (
        event.relatedTarget &&
        dropArea.contains(event.relatedTarget)
    ) {
        return;
    }

    dropArea.classList.remove("dragover");

});


/* ============================================================
   DRAG & DROP
   ============================================================ */

dropArea.addEventListener("drop", async function(event) {

    event.preventDefault();

    dropArea.classList.remove("dragover");

    const items = event.dataTransfer.items;

    if (items && items.length) {

        const entries = [];

        for (let i = 0; i < items.length; i++) {

            const item = items[i];

            if (item.kind !== "file") {
                continue;
            }

            if (
                typeof item.webkitGetAsEntry === "function"
            ) {

                const entry =
                    item.webkitGetAsEntry();

                if (entry) {
                    entries.push(entry);
                }

            } else {

                const file = item.getAsFile();

                if (file) {
                    entries.push(file);
                }

            }

        }


        if (entries.length) {

            try {

                const files =
                    await collectEntries(entries);

                if (files.length) {
                    uploadFiles(files);
                }

            } catch (error) {

                console.error(
                    "Directory reading error:",
                    error
                );

                alert(
                    "Fehler beim Lesen des Ordners."
                );

            }

            return;
        }
    }


    /* --------------------------------------------------------
       FALLBACK: NORMAL FILE DROP
       -------------------------------------------------------- */

    if (
        event.dataTransfer.files &&
        event.dataTransfer.files.length
    ) {

        const files =
            Array.from(
                event.dataTransfer.files
            );

        uploadFiles(files);

    }

});


/* ============================================================
   FILE PICKER
   ============================================================ */

fileInput.addEventListener("change", function() {

    const files =
        Array.from(fileInput.files || []);

    if (files.length) {
        uploadFiles(files);
    }

    fileInput.value = "";

});


/* ============================================================
   FOLDER PICKER
   ============================================================ */

folderInput.addEventListener("change", function() {

    const files =
        Array.from(folderInput.files || []);

    if (files.length) {
        uploadFiles(files);
    }

    folderInput.value = "";

});


/* ============================================================
   RECURSIVE DIRECTORY READER
   ============================================================ */

async function collectEntries(entries) {

    const files = [];


    async function processEntry(entry, parentPath) {

        /* ----------------------------------------------------
           FILE
           ---------------------------------------------------- */

        if (entry.isFile) {

            const file =
                await getFileFromEntry(entry);

            if (file) {

                file._homeCloudPath =
                    parentPath + entry.name;

                files.push(file);

            }

            return;
        }


        /* ----------------------------------------------------
           DIRECTORY
           ---------------------------------------------------- */

        if (entry.isDirectory) {

            const directoryPath =
                parentPath +
                entry.name +
                "/";


            const reader =
                entry.createReader();


            while (true) {

                const children =
                    await readDirectoryBatch(reader);


                if (!children.length) {
                    break;
                }


                for (const child of children) {

                    await processEntry(
                        child,
                        directoryPath
                    );

                }

            }

        }

    }


    for (const entry of entries) {

        /*
         * Normal File object
         */

        if (entry instanceof File) {

            entry._homeCloudPath =
                entry.name;

            files.push(entry);

        }

        /*
         * FileSystemEntry
         */

        else {

            await processEntry(
                entry,
                ""
            );

        }

    }


    return files;

}


/* ============================================================
   READ DIRECTORY BATCH
   ============================================================ */

function readDirectoryBatch(reader) {

    return new Promise(function(resolve, reject) {

        reader.readEntries(
            resolve,
            reject
        );

    });

}


/* ============================================================
   GET FILE FROM ENTRY
   ============================================================ */

function getFileFromEntry(entry) {

    return new Promise(function(resolve) {

        entry.file(
            function(file) {
                resolve(file);
            },
            function() {
                resolve(null);
            }
        );

    });

}


/* ============================================================
   FORMAT BYTES
   ============================================================ */

function formatBytes(bytes) {

    if (!Number.isFinite(bytes) || bytes <= 0) {
        return "0 B";
    }


    const units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ];


    let value = bytes;
    let unitIndex = 0;


    while (
        value >= 1024 &&
        unitIndex < units.length - 1
    ) {

        value /= 1024;
        unitIndex++;

    }


    if (unitIndex === 0) {

        return (
            Math.round(value) +
            " " +
            units[unitIndex]
        );

    }


    return (
        value.toFixed(1) +
        " " +
        units[unitIndex]
    );

}




function uploadFiles(files) {

    if (!files || !files.length) {
        return;
    }

    const uploadList = Array.from(files);

    let totalBytes = 0;

    for (const file of uploadList) {
        totalBytes += Number(file.size) || 0;
    }

    progressContainer.classList.add("active");

    progressBar.style.width = "0%";
    progressPercent.innerText = "0%";

    progressText.innerText = "Preparing upload...";

    progressDetails.innerText =
        "0 B / " + formatBytes(totalBytes);

    let currentIndex = 0;
    let completedBytes = 0;


    function uploadNext() {

        if (currentIndex >= uploadList.length) {

            progressBar.style.width = "100%";
            progressPercent.innerText = "100%";

            progressText.innerText =
                "Upload complete";

            progressDetails.innerText =
                formatBytes(totalBytes) +
                " / " +
                formatBytes(totalBytes);

            setTimeout(() => {
                location.reload();
            }, 800);

            return;
        }


        const file = uploadList[currentIndex];

        console.log("FILE:", file);
        console.log("FILE TYPE:", typeof file);
        console.log("FILE NAME:", file?.name);
        console.log("FILE SIZE:", file?.size);
        console.log("FILE INSTANCE:", file instanceof File);


        /*
         * Bei einem Ordner-Upload:
         *
         *   lab/loader/test.py
         *
         * Bei einer einzelnen Datei:
         *
         *   test.py
         *
         * Der absolute Mac-Pfad wird NICHT verwendet.
         */

        let relativePath =
            file.webkitRelativePath ||
            file._homeCloudPath ||
            file.name;


        /*
         * Wenn wir uns bereits innerhalb eines
         * Cloud-Ordners befinden, bleibt die Auswahl
         * relativ zu diesem Ordner.
         */


        const formData = new FormData();

        formData.append(
            "relative_path",
            relativePath
        );

        formData.append(
            "file",
            file,
            file.name
        );


        const xhr = new XMLHttpRequest();

        xhr.open(
            "POST",
            "/upload?path=" +
            encodeURIComponent(currentCloudPath),
            true
        );

        xhr.setRequestHeader(
            "X-Requested-With",
            "XMLHttpRequest"
        );


        xhr.upload.addEventListener(
            "progress",
            function(event) {

                if (!event.lengthComputable) {
                    return;
                }

                const currentFileBytes =
                    event.loaded;

                const totalUploaded =
                    completedBytes +
                    currentFileBytes;

                let percent = 0;

                if (totalBytes > 0) {

                    percent =
                        (
                            totalUploaded /
                            totalBytes
                        ) * 100;
                }

                percent =
                    Math.max(
                        0,
                        Math.min(
                            100,
                            percent
                        )
                    );

                progressBar.style.width =
                    percent.toFixed(2) + "%";

                progressPercent.innerText =
                    Math.floor(percent) + "%";

                progressText.innerText =
                    "Uploading " +
                    (currentIndex + 1) +
                    " / " +
                    uploadList.length +
                    ": " +
                    relativePath;

                progressDetails.innerText =
                    formatBytes(totalUploaded) +
                    " / " +
                    formatBytes(totalBytes);
            }
        );


        xhr.onload = function() {

            if (
                xhr.status >= 200 &&
                xhr.status < 300
            ) {

                completedBytes +=
                    Number(file.size) || 0;

                currentIndex++;

                uploadNext();

                return;
            }


            let message =
                "Upload failed:\n\n" +
                relativePath;

            try {

                const response =
                    JSON.parse(
                        xhr.responseText
                    );

                if (response.error) {

                    message +=
                        "\n\n" +
                        response.error;
                }

            } catch (error) {

                console.error(error);
            }

            progressText.innerText =
                "Upload failed";

            alert(message);
        };


        xhr.onerror = function() {

            progressText.innerText =
                "Network error";

            alert(
                "Network error while uploading:\n\n" +
                relativePath
            );
        };


        xhr.send(formData);
    }


    uploadNext();
}




/* ============================================================
   DELETE
   ============================================================ */

async function deleteItem(path) {

    if (
        !confirm(
            "Delete this item?"
        )
    ) {
        return;
    }


    try {

        const response =
            await fetch(
                "/delete",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        path: path
                    })
                }
            );


        const data =
            await response.json();


        if (data.success) {

            location.reload();

        } else {

            alert(
                data.error ||
                "Delete failed"
            );

        }

    } catch (error) {

        console.error(error);

        alert(
            "Network error while deleting."
        );

    }

}


/* ============================================================
   CREATE FOLDER
   ============================================================ */

async function createFolder() {

    const name =
        prompt(
            "Folder name:"
        );


    if (!name) {
        return;
    }


    try {

        const response =
            await fetch(
                "/mkdir",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        name: name,

                        path:
                            currentCloudPath

                    })
                }
            );


        const data =
            await response.json();


        if (data.success) {

            location.reload();

        } else {

            alert(
                data.error ||
                "Could not create folder"
            );

        }

    } catch (error) {

        console.error(error);

        alert(
            "Network error while creating folder."
        );

    }

}


/* ============================================================
   SEARCH
   ============================================================ */

function searchFiles() {

    const input =
        document.getElementById("search");


    if (!input) {
        return;
    }


    const query =
        input.value.toLowerCase();


    document
        .querySelectorAll(".file")
        .forEach(function(file) {

            const name =
                (
                    file.dataset.name ||
                    ""
                ).toLowerCase();


            file.style.display =
                name.includes(query)
                    ? ""
                    : "none";

        });

}


/* ============================================================
   GO UP
   ============================================================ */

function goUp() {

    const parts =
        currentCloudPath
            .split("/")
            .filter(Boolean);


    parts.pop();


    const parent =
        parts.join("/");


    window.location =
        "/?path=" +
        encodeURIComponent(parent);

}

</script>
"""

# ============================================================
# HELPERS
# ============================================================

def format_size(size):
    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{value:.1f} PB"


def file_icon(path: Path):
    if path.is_dir():
        return "📁"

    suffix = path.suffix.lower()

    images = {
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".png": "🖼️",
        ".gif": "🖼️",
        ".webp": "🖼️",

        ".mp4": "🎬",
        ".mov": "🎬",
        ".avi": "🎬",
        ".mkv": "🎬",

        ".mp3": "🎵",
        ".wav": "🎵",
        ".flac": "🎵",

        ".zip": "📦",
        ".rar": "📦",
        ".7z": "📦",

        ".pdf": "📕",

        ".py": "🐍",
        ".js": "📜",
        ".html": "🌐",
        ".css": "🎨",

        ".txt": "📄",
        ".md": "📝",
    }

    return images.get(suffix, "📄")


def safe_relative_upload_path(relative_path: str):
    """
    Validates a browser-provided relative file path.

    Example:

        Photos/2026/Trip/image.jpg

    becomes:

        ["Photos", "2026", "Trip", "image.jpg"]
    """

    if not relative_path:
        raise ValueError("Empty relative path")

    relative_path = relative_path.replace("\\", "/")

    parts = []

    for part in relative_path.split("/"):
        part = part.strip()

        if not part:
            continue

        if part in (".", ".."):
            raise ValueError("Invalid relative path")

        if "\x00" in part:
            raise ValueError("Invalid filename")

        parts.append(part)

    if not parts:
        raise ValueError("Invalid relative path")

    return parts


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    current_path = request.args.get(
        "path",
        ""
    )

    try:
        current_dir = safe_path(
            current_path
        )

    except ValueError:
        return "Invalid path", 400

    if not current_dir.exists():
        return "Folder not found", 404

    if not current_dir.is_dir():
        return "Not a folder", 400

    items = []

    try:
        children = sorted(
            current_dir.iterdir(),
            key=lambda p: (
                not p.is_dir(),
                p.name.lower()
            )
        )

        for child in children:
            relative = child.relative_to(
                SHARE_DIR
            )

            stat = child.stat()

            items.append({
                "name": child.name,

                "path": str(
                    relative
                ).replace(
                    "\\",
                    "/"
                ),

                "is_dir": child.is_dir(),

                "size": (
                    ""
                    if child.is_dir()
                    else format_size(
                        stat.st_size
                    )
                ),

                "modified": (
                    "-"
                    if child.is_dir()
                    else datetime.fromtimestamp(
                        stat.st_mtime
                    ).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                ),

                "icon": file_icon(
                    child
                )
            })

    except PermissionError:
        return "Permission denied", 403

    return render_template_string(
        HTML,
        items=items,
        current_path=current_path
    )


# ============================================================
# DOWNLOAD
# ============================================================

@app.route("/download")
def download():
    path = request.args.get(
        "path",
        ""
    )

    try:
        file_path = safe_path(
            path
        )

    except ValueError:
        return "Invalid path", 400

    if not file_path.exists():
        return "File not found", 404

    if not file_path.is_file():
        return "Not a file", 400

    return send_file(
        file_path,
        as_attachment=True
    )


# ============================================================
# UPLOAD
# ============================================================

@app.route("/upload", methods=["POST"])
def upload():

    upload_path = request.args.get("path", "")

    print()
    print("=" * 70)
    print("UPLOAD REQUEST")
    print("Destination:", upload_path)

    # --------------------------------------------------------
    # DESTINATION
    # --------------------------------------------------------

    try:
        destination = safe_path(upload_path)

    except ValueError as exc:
        print("DESTINATION ERROR:", exc)

        return jsonify({
            "success": False,
            "error": "Invalid destination path"
        }), 400

    print("Destination resolved:", destination)

    if not destination.exists():
        print("DESTINATION DOES NOT EXIST")

        return jsonify({
            "success": False,
            "error": "Destination folder does not exist"
        }), 400

    if not destination.is_dir():
        print("DESTINATION IS NOT A DIRECTORY")

        return jsonify({
            "success": False,
            "error": "Destination is not a folder"
        }), 400

    # --------------------------------------------------------
    # FILE
    # --------------------------------------------------------

    print("CONTENT TYPE:", request.content_type)
    print("CONTENT LENGTH:", request.content_length)
    print("FORM:", request.form)
    print("FILES:", request.files)

    if "file" not in request.files:
        print("NO FILE IN REQUEST")

        return jsonify({
            "success": False,
            "error": "No file uploaded"
        }), 400

    uploaded_file = request.files["file"]

    print("Original filename:", uploaded_file.filename)

    if not uploaded_file.filename:
        print("EMPTY FILENAME")

        return jsonify({
            "success": False,
            "error": "Invalid filename"
        }), 400

    # --------------------------------------------------------
    # RELATIVE PATH
    # --------------------------------------------------------

    relative_path = request.form.get(
        "relative_path",
        uploaded_file.filename
    )

    print("Relative path:", relative_path)

    # --------------------------------------------------------
    # SANITIZE PATH
    # --------------------------------------------------------

    try:
        parts = safe_relative_upload_path(
            relative_path
        )

    except ValueError as exc:
        print("RELATIVE PATH ERROR:", exc)

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    print("Path parts:", parts)

    filename = parts[-1]

    relative_directories = parts[:-1]

    # --------------------------------------------------------
    # BUILD DIRECTORY
    # --------------------------------------------------------

    target_directory = destination

    try:

        for directory in relative_directories:

            target_directory = (
                target_directory / directory
            )

        print(
            "Target directory:",
            target_directory
        )

        target_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    except Exception as exc:

        print(
            "DIRECTORY CREATION ERROR:",
            repr(exc)
        )

        return jsonify({
            "success": False,
            "error": (
                "Could not create destination "
                f"directory: {exc}"
            )
        }), 500

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    target = (
        target_directory / filename
    )

    print("Initial target:", target)

    # --------------------------------------------------------
    # DON'T OVERWRITE
    # --------------------------------------------------------

    if target.exists():

        stem = target.stem
        suffix = target.suffix
        counter = 1

        while target.exists():

            target = (
                target_directory /
                f"{stem} ({counter}){suffix}"
            )

            counter += 1

    print("Final target:", target)

    # --------------------------------------------------------
    # SECURITY CHECK
    # --------------------------------------------------------

    try:

        resolved_target = target.resolve()
        resolved_share = SHARE_DIR.resolve()

        resolved_target.relative_to(
            resolved_share
        )

    except ValueError:

        print("SECURITY CHECK FAILED")

        return jsonify({
            "success": False,
            "error": "Invalid upload path"
        }), 400

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        uploaded_file.save(
            str(target)
        )

        print("FILE SAVED SUCCESSFULLY")

    except Exception as exc:

        print(
            "FILE SAVE ERROR:",
            repr(exc)
        )

        return jsonify({
            "success": False,
            "error": (
                "Could not save file: "
                f"{exc}"
            )
        }), 500

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    if not target.exists():

        print("WARNING: FILE DOES NOT EXIST AFTER SAVE")

        return jsonify({
            "success": False,
            "error": "File was not created"
        }), 500

    file_size = target.stat().st_size

    print("Saved size:", file_size)
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    relative_result = target.relative_to(
        SHARE_DIR
    )

    return jsonify({

        "success": True,

        "filename": str(
            relative_result
        ).replace(
            "\\",
            "/"
        ),

        "size": file_size

    })
# ============================================================
# DELETE
# ============================================================

@app.route(
    "/delete",
    methods=["POST"]
)
def delete():

    data = request.get_json(
        silent=True
    ) or {}

    path = data.get(
        "path",
        ""
    )

    try:
        target = safe_path(
            path
        )

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid path"
        }), 400

    if not target.exists():
        return jsonify({
            "success": False,
            "error": "Item not found"
        }), 404

    if target == SHARE_DIR.resolve():
        return jsonify({
            "success": False,
            "error": "Cannot delete root folder"
        }), 400

    try:

        if target.is_dir():
            shutil.rmtree(
                target
            )

        else:
            target.unlink()

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    return jsonify({
        "success": True
    })


# ============================================================
# CREATE DIRECTORY
# ============================================================

@app.route(
    "/mkdir",
    methods=["POST"]
)
def mkdir():

    data = request.get_json(
        silent=True
    ) or {}

    name = data.get(
        "name",
        ""
    )

    current_path = data.get(
        "path",
        ""
    )

    if not name:
        return jsonify({
            "success": False,
            "error": "Folder name required"
        }), 400

    # Nur einen einzelnen Verzeichnisnamen erlauben
    name = Path(name).name

    if name in (
        "",
        ".",
        ".."
    ):
        return jsonify({
            "success": False,
            "error": "Invalid folder name"
        }), 400

    try:
        parent = safe_path(
            current_path
        )

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid path"
        }), 400

    if not parent.is_dir():
        return jsonify({
            "success": False,
            "error": "Invalid parent folder"
        }), 400

    new_folder = (
        parent / name
    )

    try:
        new_folder.mkdir(
            parents=False,
            exist_ok=False
        )

    except FileExistsError:
        return jsonify({
            "success": False,
            "error": "Folder already exists"
        }), 409

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    return jsonify({
        "success": True
    })


# ============================================================
# MAIN
# ============================================================

def home_cloud(port:int):

    ip = get_local_ip()

    print()
    print("=" * 55)
    print("                 HomeCloud")
    print("=" * 55)
    print()

    print("Share folder:")
    print(f"  {SHARE_DIR}")
    print()

    print("Local access:")
    print(f"  http://127.0.0.1:{port}")
    print()

    print("LAN access:")
    print(f"  http://{ip}:{port}")
    print()

    print("Press CTRL+C to stop the server.")
    print()

    print("=" * 55)
    print()

    app.run(
        host=HOST,
        port=port,
        threaded=True,
        debug=False
    )


const API_URL = "http://127.0.0.1:5000";  // Backend server URL
let jwtToken = "";

// Handle Login
document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
        jwtToken = data.token;
        alert("Login successful!");
        document.getElementById("login-section").style.display = "none";
        document.getElementById("file-section").style.display = "block";
    } else {
        alert("Login failed: " + data.message);
    }
});

// Handle File Upload
document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = document.getElementById("upload-file").files[0];
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${jwtToken}` },
        body: formData
    });

    const data = await response.json();
    alert(data.message || "Error uploading file.");
});

// List Files and Add Actions (Download, Modify, Delete, Rename)
document.getElementById("list-files-btn").addEventListener("click", async () => {
    const response = await fetch(`${API_URL}/files`, {
        headers: { "Authorization": `Bearer ${jwtToken}` }
    });

    const data = await response.json();
    const fileList = document.getElementById("file-list");
    fileList.innerHTML = ""; // Clear existing list

    if (data.files) {
        data.files.forEach(file => {
            // Create list item container
            const listItem = document.createElement("li");
            listItem.className = "list-group-item d-flex justify-content-between align-items-center";

            // File name
            const fileNameSpan = document.createElement("span");
            fileNameSpan.textContent = file;

            // Button Group
            const buttonGroup = document.createElement("div");

            // Download Button
            const downloadBtn = document.createElement("button");
            downloadBtn.className = "btn btn-sm btn-warning mr-2";
            downloadBtn.textContent = "Download";
            downloadBtn.onclick = () => downloadFile(file);

            // Modify Button
            const modifyBtn = document.createElement("button");
            modifyBtn.className = "btn btn-sm btn-success mr-2";
            modifyBtn.textContent = "Modify";
            modifyBtn.onclick = () => modifyFilePrompt(file);

            // Rename Button
            const renameBtn = document.createElement("button");
            renameBtn.className = "btn btn-sm btn-info mr-2";
            renameBtn.textContent = "Rename";
            renameBtn.onclick = () => renameFilePrompt(file);

            // Delete Button
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "btn btn-sm btn-danger";
            deleteBtn.textContent = "Delete";
            deleteBtn.onclick = () => deleteFile(file);

            // Append buttons to button group
            buttonGroup.appendChild(downloadBtn);
            buttonGroup.appendChild(modifyBtn);
            buttonGroup.appendChild(renameBtn);
            buttonGroup.appendChild(deleteBtn);

            // Append file name and buttons to list item
            listItem.appendChild(fileNameSpan);
            listItem.appendChild(buttonGroup);

            // Add list item to the file list
            fileList.appendChild(listItem);
        });
    } else {
        alert("Error fetching files.");
    }
});

// Download File
function downloadFile(filename) {
    fetch(`${API_URL}/download/${filename}`, {
        headers: { "Authorization": `Bearer ${jwtToken}` }
    })
    .then(response => {
        if (!response.ok) throw new Error("Error downloading file.");
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => alert(error.message));
}

// Prompt to Modify (Overwrite) File
function modifyFilePrompt(filename) {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.onchange = async () => {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_URL}/modify/${filename}`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${jwtToken}` },
            body: formData
        });

        const data = await response.json();
        alert(data.message || "Error modifying file.");
    };
    fileInput.click();
}

// Rename File
function renameFilePrompt(filename) {
    const newName = prompt("Enter the new file name:", filename);
    if (newName && newName !== filename) {
        fetch(`${API_URL}/rename/${filename}`, {
            method: "POST",
            headers: { 
                "Authorization": `Bearer ${jwtToken}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ new_name: newName })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || "Error renaming file.");
            document.getElementById("list-files-btn").click(); // Refresh list
        })
        .catch(error => alert(error.message));
    }
}

// Delete File
function deleteFile(filename) {
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
        fetch(`${API_URL}/delete/${filename}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${jwtToken}` }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || "Error deleting file.");
            document.getElementById("list-files-btn").click(); // Refresh list
        })
        .catch(error => alert(error.message));
    }
}


// Logout
document.getElementById("logout-btn").addEventListener("click", () => {
    jwtToken = "";
    document.getElementById("file-section").style.display = "none";
    document.getElementById("login-section").style.display = "block";
});

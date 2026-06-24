const API_URL = "http://127.0.0.1:8000";

export async function generatePrompt(payload) {
    const response = await fetch(`${API_URL}/generate-prompt`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error("Could not generate prompt.");
    }

    return response.json();
}

export async function saveHistory(payload) {
    const response = await fetch(`${API_URL}/save-history`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error("Could not save history.");
    }

    return response.json();
}

export async function uploadReference(file) {
    if (!file) {
        return null;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/upload-reference`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Could not upload reference image.");
    }

    const data = await response.json();
    return data.reference_image_path;
}

export async function generateImage(finalPrompt) {
    const response = await fetch(`${API_URL}/generate-image`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            final_prompt: finalPrompt,
        }),
    });

    if (!response.ok) {
        throw new Error("Could not generate image.");
    }

    return response.json();
}
export async function getHistory() {
    const response = await fetch(`${API_URL}/history`);

    if (!response.ok) {
        throw new Error("Could not load history.");
    }

    const data = await response.json();
    return data.history;
}

export async function deleteHistoryItem(historyId) {
    const response = await fetch(`${API_URL}/history/${historyId}`, {
        method: "DELETE",
    });

    if (!response.ok) {
        throw new Error("Could not delete history item.");
    }

    return response.json();
}

export async function clearHistory() {
    const response = await fetch(`${API_URL}/history`, {
        method: "DELETE",
    });

    if (!response.ok) {
        throw new Error("Could not clear history.");
    }

    return response.json();
}
export async function checkApiHealth() {
    const response = await fetch(`${API_URL}/`);

    if (!response.ok) {
        throw new Error("API is offline.");
    }

    return response.json();
}
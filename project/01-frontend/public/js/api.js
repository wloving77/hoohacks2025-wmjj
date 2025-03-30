

const BASE_API_URL = window.CONFIG?.API_BASE_URL || "http://localhost:5001";

const Endpoints = [
    `${BASE_API_URL}/api/articles`,
    `${BASE_API_URL}/api/executive`,
    `${BASE_API_URL}/api/issues`,
    `${BASE_API_URL}/api/biography`,
    `${BASE_API_URL}/api/summarize`,
];

async function defaultFetch(endpoint) {
    const url = new URL(endpoint, window.location.origin);

    try {
        const response = await fetch(url.toString(), {
            method: "GET"
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (err) {
        console.error("Error fetching results:", err);
        return null;
    }
}

async function fetchResults(endpoint, queryText, topK) {
    const url = new URL(endpoint, window.location.origin);
    url.searchParams.append("query_text", queryText);
    url.searchParams.append("top_k", topK);

    try {
        const response = await fetch(url.toString(), {
            method: "GET"
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (err) {
        console.error("Error fetching results:", err);
        return null;
    }
}

async function summarizePoliticalContext(endpoint,promptText) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt: promptText
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`API Error: ${error.error || response.statusText}`);
        }

        const data = await response.json();
        console.log("LLM Response:", data.llm_response);

        const responseDict = {
            "llm_response": data.llm_response,
            "articles": data.articles,
            "executive_orders": data.executive_orders,
        }

        return responseDict;

    } catch (error) {
        console.error("Failed to summarize political context:", error);
        return null;
    }
}


async function fetchArticles(queryText, topK) {
    return await fetchResults(Endpoints[0], queryText, topK);
}

async function fetchExecutive(queryText, topK) {
    return await fetchResults(Endpoints[1], queryText, topK);
}

async function fetchIssues() {
    return await defaultFetch(Endpoints[2]);
}

async function fetchBiography(queryText, topK) {
    return await fetchResults(Endpoints[3], queryText, topK);
}

async function fetchSummary(promptText) {
    return await summarizePoliticalContext(Endpoints[4], promptText);
}


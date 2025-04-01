import google.generativeai as genai
from flask import jsonify, current_app
from app.services.embedding import (
    similarity_search_articles,
    similarity_search_executive,
)


def initialize_llm_model():
    api_key = current_app.config["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-pro-002")


def gemini_summarize(request):

    # Initialize LLM
    llm_model = initialize_llm_model()

    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    prompt = data["prompt"]
    articles = similarity_search_articles(prompt, top_k=10)
    executives = similarity_search_executive(prompt, top_k=10)

    pre_prompt = (
        "You are a political assistant. The user has shared a personal or professional concern.\n\n"
        "Use the attached articles and executive orders to explain how recent political developments may affect them. Base your answer only on those documents.\n\n"
        "Article Summaries will be appended after the user prompt below.\n\n"
        "Respond using RAW HTML, not Markdown. Do not wrap your output in backticks or escape characters. Do not include <html>, <head>, or <body> tags.\n\n"
        'Use semantic HTML elements: <section>, <h2>, <h3>, <ul>, <li>, <p>, <strong>. Apply Tailwind utility classes where helpful for spacing and clarity (e.g., class="mb-4", class="font-semibold", etc.), but use your judgment to adapt the layout to the content.\n\n'
        "Follow the structure below, but you may adapt or reorganize content sections if needed to best serve the user's question:\n\n"
        "---\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">User or Issue Summary</h2>\n'
        "  <p>Summary of the user or issue</p>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Key Implications</h2>\n'
        '  <h3 class="text-lg font-medium">How This May Affect the User</h3>\n'
        '  <ul class="list-disc pl-6 space-y-2">\n'
        "    <li>Explain a specific impact</li>\n"
        "    <li>Another important implication</li>\n"
        "    <li>Optional additional point</li>\n"
        "  </ul>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Policy Context</h2>\n'
        '  <h3 class="text-lg font-medium">Relevant Articles</h3>\n'
        "  <p><strong>Title 1:</strong> Summary...</p>\n"
        "  <p><strong>Title 2:</strong> Summary...</p>\n"
        '  <h3 class="text-lg font-medium mt-4">Relevant Executive Orders</h3>\n'
        "  <p><strong>EO Title 1:</strong> Summary...</p>\n"
        "  <p><strong>EO Title 2:</strong> Summary...</p>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Recommendations</h2>\n'
        '  <ul class="list-disc pl-6 space-y-2">\n'
        "    <li><strong>Stay Informed:</strong> Describe useful sources or topics to watch</li>\n"
        "    <li><strong>Consider Actions:</strong> Strategic career or personal steps</li>\n"
        "    <li><strong>Engage Locally:</strong> Civic/union/community involvement ideas</li>\n"
        "  </ul>\n"
        "</section>\n\n"
        '<section class="mb-6">\n'
        '  <h2 class="text-xl font-semibold">Supporting Sources</h2>\n'
        '  <ul class="list-disc pl-6 space-y-2">\n'
        "    <li>List article or EO titles if relevant</li>\n"
        "  </ul>\n"
        "</section>\n\n"
        "Write clearly and professionally, adapting your tone to the user's context. Do not mention that you are an AI model."
        "If it is obviously not a user and simply a political issue, summarize that political issue with respect to the articles and executive orders"
        "Do not fill null for anything. You are meant to be informative. Thanks!\n\n"
    )
    final_prompt = f"{pre_prompt}\n\n{prompt}"

    # Append LLM summaries for articles
    for article in articles:
        content = article.get("summary", "")
        article["llm_synopses"] = llm_model.generate_content(
            "Relevant article: " + content
        ).text

    for order in executives:
        content = order.get("summary", "")
        order["llm_synopses"] = llm_model.generate_content(
            "Relevant executive order: " + content
        ).text

    final_prompt += "\n\n" + "\n\n".join(
        [f"{a['name']}: {a['llm_synopses']}" for a in articles]
    )
    final_prompt += "\n\n" + "\n\n".join(
        [f"{e['name']}: {e['llm_synopses']}" for e in executives]
    )

    try:
        response = llm_model.generate_content(final_prompt).text
        return jsonify(
            {
                "llm_response": response,
                "articles": articles,
                "executive_orders": executives,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

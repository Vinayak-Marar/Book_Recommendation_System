from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle

app = Flask(__name__)

# =========================
# Load trained model
# =========================
with open('model_data.pkl', 'rb') as f:
    data = pickle.load(f)

P = data['P']
Q = data['Q']
user_map = data['user_map']
book_map = data['book_map']
book_df = data['book_df']


# =========================
# Create new user vector
# =========================
def create_new_user_vector(liked_isbns):
    vectors = []

    for isbn in liked_isbns:
        isbn = isbn.strip()
        if isbn in book_map:
            b = book_map[isbn]
            vectors.append(Q[b])

    if len(vectors) == 0:
        return None

    return np.mean(vectors, axis=0)


# =========================
# Recommend books
# =========================
def recommend_for_new_user(liked_isbns, top_n=10):
    user_vector = create_new_user_vector(liked_isbns)

    if user_vector is None:
        return []

    scores = np.dot(Q, user_vector)

    liked_indices = [book_map[i] for i in liked_isbns if i in book_map]
    scores[liked_indices] = -np.inf

    top_indices = np.argsort(scores)[-top_n:][::-1]

    # Convert matrix indices → ISBNs safely
    index_to_isbn = {v: k for k, v in book_map.items()}

    recommended_isbns = [
        index_to_isbn[i]
        for i in top_indices
        if i in index_to_isbn
    ]

    # Now filter dataframe by ISBN instead of iloc
    recommendations = book_df[
        book_df['ISBN'].isin(recommended_isbns)
    ][['ISBN', 'Title', 'Author']]

    return recommendations.to_dict(orient='records')


# =========================
# Autocomplete API
# =========================
@app.route('/search')
def search():
    query = request.args.get('q', '').lower()

    if not query:
        return jsonify([])

    matches = book_df[
        book_df['Title'].str.lower().str.contains(query, na=False)
    ].head(10)

    results = matches[['ISBN', 'Title', 'Author']] \
        .to_dict(orient='records')

    return jsonify(results)


# =========================
# Main Page
# =========================
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []

    if request.method == 'POST':
        liked_isbns = request.form['isbns'].split(',')
        recommendations = recommend_for_new_user(liked_isbns)

    return render_template(
        'index.html',
        recommendations=recommendations
    )


if __name__ == '__main__':
    app.run(debug=True)

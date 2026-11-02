from flask import Flask, render_template, request, redirect, url_for, flash
from db import create_connection

app = Flask(__name__)
app.secret_key = "pippergeddon"

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books_per_page = 5
    offset = (page - 1) * books_per_page

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total_books FROM books')
    total_books = cursor.fetchone()['total_books']
    total_pages = (total_books + books_per_page - 1) // books_per_page

    cursor.execute('SELECT * FROM books LIMIT %s OFFSET %s', (books_per_page, offset))
    books = cursor.fetchall()
    connection.close()

    return render_template('index.html', books=books, page=page, total_pages=total_pages)

@app.route('/add', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO books (title, author, year) VALUES (%s, %s, %s)',
            (title, author, year)
        )
        connection.commit()
        connection.close()

        flash('Libro agregado exitosamente')
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_book(id):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM books WHERE id = %s', (id,))
    book = cursor.fetchone()
    connection.close()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            'UPDATE books SET title = %s, author = %s, year = %s WHERE id = %s',
            (title, author, year, id)
        )
        connection.commit()
        connection.close()

        flash('Libro actualizado exitosamente')
        return redirect(url_for('index'))

    return render_template('edit_book.html', book=book)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_book(id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s', (id,))
    connection.commit()
    connection.close()

    flash('Libro eliminado exitosamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

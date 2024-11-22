#!/usr/bin/python3
import json
import uuid
import argparse
import dataclasses
from typing import List, Optional
from dataclasses import dataclass


class BookNotFoundError(BaseException):
    pass


@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    status: str = 'В наличии'


def init_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
            description='Books manager'
    )
    
    subparsers = parser.add_subparsers(title='subcommands', required=True, dest='subcommand')

    # add a add subcommand ;)
    subcommand_parser = subparsers.add_parser(
            name='add',
            help='add a book',
            description='Add a book.'
    )
    subcommand_parser.add_argument('title',  type=str, help='book title')
    subcommand_parser.add_argument('author', type=str, help='book author')
    subcommand_parser.add_argument('year',   type=int, help='publication year')

    # add a del subcommand
    subcommand_parser = subparsers.add_parser(
            name='delete', 
            help='delete a book',
            description='Delete a book by id.'
    )
    subcommand_parser.add_argument('id', type=int, help='book id')

    # add a search subcommand
    subcommand_parser = subparsers.add_parser(
            name='search', 
            help='search for a book in the database', 
            description='Search for a book by title and/or author and/or year of publication.'
    )
    subcommand_parser.add_argument('-t', '--title',  type=str, help='book title')
    subcommand_parser.add_argument('-a', '--author', type=str, help='book author')
    subcommand_parser.add_argument('-y', '--year',   type=int, help='publication year')
   
    # add a list subcommand
    subcommand_parser = subparsers.add_parser(
            name='list',
            help='show books from the database',
            description='Show books from the database.'
    )
   
    # add a status subcommand
    subcommand_parser = subparsers.add_parser(
            name='status',   
            help='update the status of the book',
            description='Update the status of the book.'
    )
    subcommand_parser.add_argument('id',         type=int, help='book id')
    subcommand_parser.add_argument('new_status', type=str, help='new status')
    
    return parser


def list_books() -> List[Book]:
    try:
        with open('books.json', 'r', encoding='UTF-8') as file:
            data = json.load(file)
        return [Book(**book) for book in data]
    except FileNotFoundError:
        return [] 


def save_books(books: List[Book]) -> None:
    with open('books.json', 'w', encoding='UTF-8') as file:
        json.dump([dataclasses.asdict(book) for book in books], file, indent=4)


def add_book(title: str, author: str, year: int) -> int:
    book = Book(uuid.uuid4().int, title, author, year)
    
    books = list_books() 
    books.append(book)
    save_books(books)
     
    return book.id


def delete_book(book_id: int) -> None:
    books = list_books()
    
    book_index = None
    for index, book in enumerate(books):
        if book.id == book_id:
            book_index = index
            break
    else:
        raise BookNotFoundError()

    del books[book_index]
    save_books(books)


def search_book(
        title: Optional[str] = None, 
        author: Optional[str] = None, 
        year: Optional[int] = None,
) -> List[Book]:

    def check_book(book: Book) -> bool:
        return all((
            not title or book.title == title,
            not author or book.author == author,
            not year or book.year == year,
        ))

    books = list_books()
    selected_books = list(filter(check_book, books))
    return selected_books


def update_book_status(book_id: int, new_status: str) -> None:
    books = list_books()

    for book in books:
        if book.id == book_id:
            book.status = new_status
            break
    else:
        raise BookNotFoundError()
    
    save_books(books)


def print_books(books: List[Book]) -> None:
    print('Books:')
    #print(f'      {"ID":<40} | TITLE by AUTHOR (YEAR) - STATUS')
    for book in books:
        print(f'    • {book.id:<40} | {book.title} by {book.author} ({book.year}) - {book.status}')


def main() -> int:
    parser = init_args_parser()
    args = parser.parse_args()
    if args.subcommand == 'add':
        book_id = add_book(args.title, args.author, args.year)
        print(f'INFO: The book has been successfully added with id `{book_id}`')
    elif args.subcommand == 'del':
        try:
            delete_book(args.id)
            print('INFO: The book has been successfully deleted.')
        except BookNotFoundError:
            print('ERROR: Book not found!')
    elif args.subcommand == 'search':
        if all((not args.title, not args.author, not args.year)):
            parser.error('No options was provided. Use -h to full information about subcommand.')
            
        books = search_book(args.title, args.author, args.year)
        if books:
            print_books(books)
        else:
            print('INFO: No books was found.')
    elif args.subcommand == 'list':
        books = list_books()
        if books:
            print_books(books)
        else:
            print('INFO: No books in database yet.')
    elif args.subcommand == 'status':
        try:
            update_book_status(args.id, args.new_status)
        except BookNotFoundError:
            print('ERROR: The book was not found!')

    return 0


if __name__ == '__main__':
    exit(main())

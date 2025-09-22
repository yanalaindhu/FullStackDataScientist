import os
from datetime import datetime, timedelta
from collections import Counter
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY in .env file")
sb: Client = create_client(url, key)
def add_member():
    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip()
    data = {"name": name, "email": email}
    resp = sb.table("members").insert(data).execute()
    print("Member added:", resp.data)

def add_book():
    title = input("Enter title: ").strip()
    author = input("Enter author: ").strip()
    category = input("Enter category: ").strip()
    stock = int(input("Enter stock count: ").strip())
    data = {"title": title, "author": author, "category": category, "stock": stock}
    resp = sb.table("books").insert(data).execute()
    print("Book added:", resp.data)

def list_books():
    resp = sb.table("books").select("*").execute()
    for book in resp.data:
        print(book)

def search_books():
    column = input("Search by (title/author/category): ").strip().lower()
    keyword = input("Enter keyword: ").strip()
    resp = sb.table("books").select("*").ilike(column, f"%{keyword}%").execute()
    for book in resp.data:
        print(book)

def update_stock():
    book_id = int(input("Enter book ID: ").strip())
    new_stock = int(input("Enter new stock: ").strip())
    resp = sb.table("books").update({"stock": new_stock}).eq("book_id", book_id).execute()
    print("Book updated:", resp.data)

def update_member():
    member_id = int(input("Enter member ID: ").strip())
    new_email = input("Enter new email: ").strip()
    resp = sb.table("members").update({"email": new_email}).eq("member_id", member_id).execute()
    print("Member updated:", resp.data)

def delete_member():
    member_id = int(input("Enter member ID to delete: ").strip())
    borrow = sb.table("borrow_records").select("*").eq("member_id", member_id).is_("return_date", None).execute().data
    if borrow:
        print("Cannot delete member with active borrowed books.")
        return
    resp = sb.table("members").delete().eq("member_id", member_id).execute()
    print("Member deleted:", resp.data)

def delete_book():
    book_id = int(input("Enter book ID to delete: ").strip())
    borrow = sb.table("borrow_records").select("*").eq("book_id", book_id).is_("return_date", None).execute().data
    if borrow:
        print("Cannot delete book that is currently borrowed.")
        return
    resp = sb.table("books").delete().eq("book_id", book_id).execute()
    print("Book deleted:", resp.data)

def borrow_book():
    member_id = int(input("Enter member ID: ").strip())
    book_id = int(input("Enter book ID: ").strip())
    book = sb.table("books").select("*").eq("book_id", book_id).single().execute().data
    if not book or book["stock"] < 1:
        print("Book not available.")
        return
    sb.table("books").update({"stock": book["stock"] - 1}).eq("book_id", book_id).execute()
    record = {"member_id": member_id, "book_id": book_id}
    sb.table("borrow_records").insert(record).execute()
    print("Book borrowed.")

def return_book():
    member_id = int(input("Enter member ID: ").strip())
    book_id = int(input("Enter book ID: ").strip())
    borrow = sb.table("borrow_records")\
        .select("*")\
        .eq("member_id", member_id)\
        .eq("book_id", book_id)\
        .is_("return_date", None)\
        .single().execute().data
    if not borrow:
        print("No active borrow record found.")
        return
    sb.table("borrow_records")\
        .update({"return_date": datetime.utcnow().isoformat()})\
        .eq("record_id", borrow["record_id"]).execute()
    book = sb.table("books").select("*").eq("book_id", book_id).single().execute().data
    sb.table("books").update({"stock": book["stock"] + 1}).eq("book_id", book_id).execute()
    print("Book returned.")

def overdue_books():
    threshold = datetime.utcnow() - timedelta(days=14)
    resp = sb.table("borrow_records")\
        .select("*")\
        .lt("borrow_date", threshold.isoformat())\
        .is_("return_date", None).execute()
    print("Overdue books:")
    for record in resp.data:
        print(record)

def most_borrowed():
    resp = sb.table("borrow_records").select("book_id").execute()
    books = [record["book_id"] for record in resp.data]
    counter = Counter(books)
    print("Top 5 borrowed books:")
    for book_id, count in counter.most_common(5):
        print(f"Book ID {book_id}: {count} times")

def books_per_member():
    resp = sb.table("borrow_records").select("member_id").execute()
    members = [record["member_id"] for record in resp.data]
    counter = Counter(members)
    print("Books borrowed per member:")
    for member_id, count in counter.items():
        print(f"Member ID {member_id}: {count} books")
def menu():
    while True:
        print("\nLibrary Management System")
        print("1. Add Member")
        print("2. Add Book")
        print("3. List Books")
        print("4. Search Books")
        print("5. Update Stock")
        print("6. Update Member Info")
        print("7. Delete Member")
        print("8. Delete Book")
        print("9. Borrow Book")
        print("10. Return Book")
        print("11. Overdue Books Report")
        print("12. Most Borrowed Books Report")
        print("13. Books Borrowed Per Member Report")
        print("0. Exit")
        
        choice = input("Enter choice: ").strip()
        
        if choice == "1":
            add_member()
        elif choice == "2":
            add_book()
        elif choice == "3":
            list_books()
        elif choice == "4":
            search_books()
        elif choice == "5":
            update_stock()
        elif choice == "6":
            update_member()
        elif choice == "7":
            delete_member()
        elif choice == "8":
            delete_book()
        elif choice == "9":
            borrow_book()
        elif choice == "10":
            return_book()
        elif choice == "11":
            overdue_books()
        elif choice == "12":
            most_borrowed()
        elif choice == "13":
            books_per_member()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
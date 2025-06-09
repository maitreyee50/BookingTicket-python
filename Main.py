import pymysql as py
from datetime import date
import random
import qrcode


mydb = py.connect(
    host="localhost",
    user="root",
    password="12345",
    database="bookmyticket"
)

mycursor = mydb.cursor()

def generate_unique_booking_id():
    while True:
        booking_id = random.randint(1000000, 9999999)
        mycursor.execute("SELECT COUNT(*) FROM bookingdts WHERE booking_id = %s", (booking_id,))
        if mycursor.fetchone()[0] == 0:
            return booking_id

def show_running_movies():
    query = """
    SELECT m.movie_name, m.movie_lang, m.theater_no, m.movie_time, 
           s.gold_price, s.platinum_price 
    FROM movies m 
    JOIN seat_capacity s ON m.theater_no = s.theater_no
    """
    mycursor.execute(query)
    myresult = mycursor.fetchall()

    print(f"{'Movie Name':<25} {'Language':<15} {'Theater No':<15} {'Show Time':<15} {'Gold Price':<20} {'Platinum Price':<20}")
    print("-" * 110)
    for row in myresult:
        movie_name, movie_lang, theater_no, movie_time, gold_price, platinum_price = row
        print(f"{movie_name:<25} {movie_lang:<15} {theater_no:<15} {movie_time:<15} {gold_price:<20} {platinum_price:<20}")
    print()

def payment(amount):
    upi_id = "roises14@okhdfcbank"  
    payee_name = "Maitreyee Saha"
    rs = amount  # Default amount in INR


    upi_url = (
        f"upi://pay?pa={upi_id}&pn={payee_name}"
        f"&am={rs}&cu=INR"
    )


    qr = qrcode.make(upi_url)
    qr.show()





def book_movie_tickets():
    total_cost = 0
    seat_capacity_bool = True

    name = input("Enter your name: ").strip()
    moviename = input("Enter movie name: ").strip()
    seatType = input("Enter the type of seat you would like (gold/platinum): ").strip().lower()

    while seatType not in ("gold", "platinum"):
        seatType = input("Invalid seat type. Enter 'gold' or 'platinum': ").strip().lower()

    while True:
        no_of_seat = input("Enter the number of seats you need: ").strip()
        if no_of_seat.isdigit() and int(no_of_seat) > 0:
            noSeats = int(no_of_seat)
            break
        else:
            print("Please enter a valid positive integer.")

    query = "SELECT movie_name, theater_no, movie_time FROM movies WHERE movie_name = %s"
    mycursor.execute(query, (moviename,))
    myresult = mycursor.fetchone()

    if not myresult:
        print("Movie not found.")
        return

    movie_name, theater_no, movie_time = myresult

    price_query = "SELECT gold_price, platinum_price FROM seat_capacity WHERE theater_no = %s"
    mycursor.execute(price_query, (theater_no,))
    price_result = mycursor.fetchone()

    if not price_result:
        print("Could not fetch seat prices.")
        return

    gold_price, platinum_price = price_result

    if seatType == 'gold':
        print(f"Price per Gold seat: ₹{gold_price}")
        total_cost = gold_price * noSeats
    else:
        print(f"Price per Platinum seat: ₹{platinum_price}")
        total_cost = platinum_price * noSeats

    seat_check_query = "SELECT left_gold, left_platinum FROM seat_capacity WHERE theater_no = %s"
    mycursor.execute(seat_check_query, (theater_no,))
    seat_availability = mycursor.fetchone()

    if not seat_availability:
        print("Theater not found.")
        return

    left_gold, left_platinum = seat_availability

    if seatType == 'gold' and noSeats > left_gold:
        print(f"Only {left_gold} gold seats are available.")
        seat_capacity_bool = False
    elif seatType == 'platinum' and noSeats > left_platinum:
        print(f"Only {left_platinum} platinum seats are available.")
        seat_capacity_bool = False

    today = date.today()

    if seat_capacity_bool:
        booking_id = generate_unique_booking_id()

        insertquery = """
        INSERT INTO bookingdts 
        (person_name, bk_moviename, theaterno, showtime, seat_type, no_of_seat, payments, date_time, booking_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (name, moviename, theater_no, movie_time, seatType, noSeats, total_cost, today, booking_id)
        mycursor.execute(insertquery, values)

        if seatType == "gold":
            update_seat_query = "UPDATE seat_capacity SET left_gold = left_gold - %s WHERE theater_no = %s"
            mycursor.execute(update_seat_query, (noSeats, theater_no))
        else:
            update_seat_query = "UPDATE seat_capacity SET left_platinum = left_platinum - %s WHERE theater_no = %s"
            mycursor.execute(update_seat_query, (noSeats, theater_no))

        mydb.commit()
        
        print(f"Ticket booked successfully! Your Booking ID is: {booking_id} , Now pay your amount\n")
        payment(total_cost)
    else:
        print("Booking failed due to insufficient seats.\n")
        


def show_ticket():
    name = input("Enter your name: ")
    query = "SELECT person_name, bk_moviename, theaterno, showtime, seat_type, no_of_seat, booking_id FROM bookingdts WHERE person_name = %s"
    mycursor.execute(query, (name,))
    result = mycursor.fetchall()
    
    for row in result:
        data = (
    f"Name: {row[0]}\n"
    f"Movie: {row[1]}\n"
    f"Theater No: {row[2]}\n"
    f"Show time: {row[3]}\n"
    f"Seat Type: {row[4]}\n"
    f"No. of Seats: {row[5]}\n"
    f"Booking ID: {row[6]}"
)

        qr_image = qrcode.make(data)
        qr_image.show()

while True:
    print("1. Show all running movies.")
    print("2. Book movie tickets.")
    print("3. Show my ticket.")
    print("4. Exit")
    try:
        main_menu_choice = int(input("Enter your choice: ").strip())
    except ValueError:
        print("Invalid input. Please enter a number from 1 to 4.\n")
        continue

    if main_menu_choice == 1:
        show_running_movies()
    elif main_menu_choice == 2:
        book_movie_tickets()
    elif main_menu_choice == 3:
        show_ticket()
    elif main_menu_choice == 4:
        print("Thank you for using BookMyTicket!")
        break
    else:
        print("Invalid choice. Please enter a number from 1 to 4.\n")

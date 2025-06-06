import pymysql as py

mydb = py.connect(
    host="localhost",
    user="root",
    password="12345",
    database="bookmyticket"
)

mycursor = mydb.cursor()

def show_running_movies():
    #query = "SELECT movie_name, movie_lang, theater_no, movie_time FROM movies"
    query="SELECT m.movie_name, m.movie_lang, m.theater_no, m.movie_time, s.gold_price, s.platinum_price FROM movies m JOIN seat_capacity s ON m.theater_no = s.theater_no"

    mycursor.execute(query)
    myresult = mycursor.fetchall()
    
    print(f"{'Movie Name':<25} {'Language':<15} {'Theater No':<15} {'Show Time':<15} {'Gold Price':<20} {'Platinum Price':<20}")
    print("-" * 110)
    for row in myresult:
        movie_name, movie_lang, theater_no, movie_time, gold_price,platinum_price = row
        print(f"{movie_name:<25} {movie_lang:<15} {theater_no:<15} {movie_time:<15} {gold_price:<20} {platinum_price:<20}")
    print()

def book_movie_tickets():
    total_cost=0
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
    
    price_query = f"SELECT gold_price, platinum_price FROM seat_capacity WHERE theater_no = %s"
   
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
        
    
    
    if seat_capacity_bool == True:
        insertquery = "INSERT INTO bookingdts (person_name, bk_moviename, theaterno, showtime, seat_type, no_of_seat,payments) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (name, moviename, theater_no, movie_time, seatType, noSeats,total_cost)
        mycursor.execute(insertquery, values)

        if seatType == "gold":
            update_seat_query = "UPDATE seat_capacity SET left_gold = left_gold - %s WHERE theater_no = %s"
            mycursor.execute(update_seat_query, (noSeats, theater_no))
        else:
            update_seat_query = "UPDATE seat_capacity SET left_platinum = left_platinum - %s WHERE theater_no = %s"
            mycursor.execute(update_seat_query, (noSeats, theater_no))

        mydb.commit()
        print("Ticket booked and seat count updated successfully!\n")
    

    
while True:
    print("1. Show all running movies.")
    print("2. Book movie tickets.")
    print("3. Exit")
    try:
        main_menu_choice = int(input("Enter your choice: ").strip())
    except ValueError:
        print("Invalid input. Please enter a number from 1 to 3.\n")
        continue

    if main_menu_choice == 1:
        show_running_movies()
    elif main_menu_choice == 2:
        book_movie_tickets()
    elif main_menu_choice == 3:
        print("Thank you for using BookMyTicket!")
        break
    else:
        print("Invalid choice. Please enter a number from 1 to 3.\n")

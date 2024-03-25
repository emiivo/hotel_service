# Hotel

# Usage:

Launch:

```git clone```

```cd hotel_service```

```docker-compose up```

# Create:

Add a resident. Only works when the room capacity is not at the limit.

```curl -X POST -H "Content-Type: application/json" -d '{"name": "John", "surname": "Doe", "room_id": 1}' http://localhost:5000/add_resident```

Create a new room.

```curl -X POST -H "Content-Type: application/json" -d '{"room_name": "Standard room", "price": 100, "size": 2}' http://localhost:5000/add_room```


# Read:

Rooms:

```curl http://localhost:5000/get_rooms```

Residents:

```curl http://localhost:5000/get_residents```

What residents occupy rooms:

```curl http://localhost:5000/get_who_lives_where```

# Update:

Update room info - name, price, size:

```curl -X POST -H "Content-Type: application/json" -d '{"room_id": 3, "new_name": "Changed room", "new_price": 1000, "new_size": 5}' http://localhost:5000/update_room```

Update resident info - move to another room:
```curl -X POST -H "Content-Type: application/json" -d "{\"resident_id\": 2, \"new_room_id\": 3}" http://localhost:5000/move_resident```


# DELETE:

Remove a room and its residents (number at the end is room id):

```curl -X DELETE http://localhost:5000/remove_room/1```

Remove a resident from a room:

```curl -X DELETE http://localhost:5000/remove_resident/1 (number at the end is resident id)```




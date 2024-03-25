from flask import Flask, render_template, request, jsonify
from hotel import Hotel

app = Flask(__name__)
hotel = Hotel()  # Initialize your hotel instance

# Get resident info
@app.route('/get_residents', methods=['GET'])
def get_residents_info():
	residents_data = [
	{
		'id': resident.id,
		'name': resident.name,
		'surname': resident.surname
	} 
	for resident in hotel.residents
	]

	return jsonify({'residents': residents_data})

# Get room info
@app.route('/get_rooms', methods=['GET'])
def get_rooms_info():
	rooms_data = [
	{
		'id': room.id,
		'name': room.room_name,
		'price': room.price,
		'size': room.size
	} 
	for room in hotel.rooms
	]

	return jsonify({'rooms': rooms_data})

# Get info of room and its residents
@app.route('/get_who_lives_where', methods=['GET'])
def get_rooms():
	rooms_residents = []
	for room in hotel.rooms:
		rooms_residents.append({
			'room_name': room.room_name,
			'price': room.price,
			'size': room.size,
			'residents': [resident.name for resident in room.lives_here]
		})
	return jsonify({'rooms': rooms_residents})


# Remove resident from a room
@app.route('/remove_resident/<int:resident_id>', methods=['DELETE'])
def remove_resident(resident_id):
	# Call the remove_resident_from_room function from the Hotel instance
	removal_result = hotel.remove_resident_from_room(resident_id)

	if removal_result:
		return jsonify({'message': f'Resident removed from room successfully'}), 200
	else:
		return (
			jsonify({'error': f'Resident with ID {resident_id} '
						'not found or lives in another room'}), 404
		)


# Remove a room along with its residents
@app.route('/remove_room/<int:room_id>', methods=['DELETE'])
def remove_room(room_id):
	if hotel.remove_room(room_id):
		return jsonify({'message': f'Room with ID {room_id} and its residents removed successfully'}), 200
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Add resident to a room
@app.route('/add_resident', methods=['POST'])
def add_resident():
	data = request.json
	name = data.get('name')
	surname = data.get('surname')
	room_id = data.get('room_id')

	# Check if the room has enough space
	room = next((room for room in hotel.rooms if room.id == room_id), None)
	if room:
		if len(room.lives_here) >= room.size:
			return jsonify({'error': 'Room is already full. Cannot add resident.'}), 400

		# Call from hotel.py
		hotel.move_resident_into_room(name, surname, room_id)

		return jsonify({'message': f'Resident added to room successfully'}), 200
    
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Create a new room
@app.route('/add_room', methods=['POST'])
def add_room():
	data = request.json
	room_name = data.get('room_name')
	price = data.get('price')
	size = data.get('size')

	hotel.create_new_room(room_name, price, size)

	return jsonify({'message': 'New room added'})

# Update a room's information
@app.route('/update_room', methods=['POST'])
def update_room():
	data = request.json
	room_id = data.get('room_id')
	new_name = data.get('new_name')
	new_price = data.get('new_price')
	new_size = data.get('new_size')
    
	success = hotel.update_room(room_id, new_name, new_price, new_size)
	if success:
		return jsonify({'message': f'Room updated successfully'}), 200
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404
        
# Move a resident from one room to another
@app.route('/move_resident', methods=['POST'])
def move_resident():
	data = request.json
	resident_id = data.get('resident_id')
	new_room_id = data.get('new_room_id')


	new_room = next((room for room in hotel.rooms if room.id == new_room_id), None)

	if not new_room:
		return jsonify({'error': 'Room not found with provided ID.'}), 404

	# Check if the new room has enough space
	if len(new_room.lives_here) >= new_room.size:
		return jsonify({'error': 'Room is already full. Cannot add resident.'}), 400
		
	# Check if the resident is already in the new room
	if any(resident.id == resident_id for resident in new_room.lives_here):
		return jsonify({'error': 'Resident is already in the new room.'}), 400


	# Call from hotel.py
	success = hotel.move_resident_into_room(resident_id, new_room_id)

	if success:
		return jsonify({'message': 'Resident moved to new room successfully'}), 200
	else:
		return jsonify({'error': 'Failed to move resident. Resident or rooms not found.'}), 404

# Define route for rendering the index page
@app.route('/')
def index():
	rooms_data = []
	for room in hotel.rooms:
		room_info = {
			'id': room.id,
			'name': room.room_name,
			'price': room.price,
			'size': room.size,
			'residents': [{'id': resident.id, 'name': resident.name, 'surname': resident.surname} for resident in room.lives_here]
		}
		rooms_data.append(room_info)

	return render_template('index.html', rooms_data=rooms_data)


	return render_template('index.html', rooms_data=rooms_data)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)

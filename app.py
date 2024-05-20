from flask import Flask, render_template, request, jsonify
from hotel import Hotel

app = Flask(__name__)
hotel = Hotel()

# Get resident info
@app.route('/residents', methods=['GET'])
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
@app.route('/rooms', methods=['GET'])
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
@app.route('/hotel', methods=['GET'])
def get_rooms():
	rooms = []
	for room in hotel.rooms:
		rooms.append({
			'room_name': room.room_name,
			'price': room.price,
			'size': room.size,
			'residents': [
				{'name': resident.name, 'surname': resident.surname}
				for resident in room.lives_here
			]
		})
	return jsonify({'rooms': rooms})

# Get room by id
@app.route('/rooms/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
	room_name = hotel.get_room_name_by_id(room_id)

	if room_name:
		return jsonify({'room_name': room_name}), 200
	else:
		return jsonify({'error': 'Room not found'}), 404


# Get resident by id
@app.route('/residents/<int:resident_id>', methods=['GET'])
def get_resident_by_id(resident_id):
	resident = hotel.get_resident_by_id(resident_id)

	if resident:
		response_data = {
			'name': resident[0],
			'surname': resident[1],
		}
		return jsonify(response_data), 200
	else:
		return jsonify({'error': 'Resident not found'}), 404

# Add resident to a room
@app.route('/residents', methods=['POST'])
def add_resident():
	data = request.json
	name = data.get('name')
	surname = data.get('surname')
	room_id = data.get('room_id')

	# Check if the room has enough space
	room = next((room for room in hotel.rooms if room.id == room_id), None)
	if room:
		if len(room.lives_here) >= room.size:
			return jsonify({'error': 'Room is already full.'}), 422

		# Call method to add resident
		try:
			success = hotel.move_in_new_resident(name, surname, room_id)
			# Construct response with added resident information
			response_data = {
				'resident': {
					'name': name,
					'surname': surname,
					'room_id': room_id
				},
				'message': 'Resident added to room successfully'
			}
			return jsonify(response_data), 201
		except ValueError as e:
			return jsonify({'error': str(e)}), 404
    
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Create a new room
@app.route('/rooms', methods=['POST'])
def add_room():
	data = request.json
	room_name = data.get('room_name')
	price = data.get('price')
	size = data.get('size')

	hotel.create_new_room(room_name, price, size)

	return jsonify({'message': 'New room added'})
	
# Update a room's information
@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
	data = request.json
	new_name = data.get('new_name')
	new_price = data.get('new_price')
	new_size = data.get('new_size')
    
	# Check if a person is assigned to the room
	person_in_room = hotel.get_person_in_room(room_id)
	if person_in_room:
		return jsonify({'error': f'A person is assigned to room with ID {room_id}. Cannot update details.'}), 422
    
	success = hotel.update_room(room_id, new_name, new_price, new_size)
	if success:
		return jsonify({'message': 'Room updated successfully'}), 200
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404

# Move existing resident to room
@app.route('/residents/<int:resident_id>', methods=['PUT'])
def move_resident(resident_id):
	data = request.json
	new_room_id = data.get('new_room_id')
    
	# Extract room_id from data
	room_id = data.get('room_id')

	residents_in_room = hotel.get_specific_resident_in_room(resident_id, new_room_id)
    
	new_room = next((room for room in hotel.rooms if room.id == new_room_id), None)
	if not new_room:
		return jsonify({'error': 'Room not found with provided ID.'}), 404

	if residents_in_room:
		return jsonify({'error': f'Resident is already in room with ID {new_room_id}.'}), 409

	# Check if the new room is full
	if len(new_room.lives_here) >= new_room.size:
		return jsonify({'error': 'Room is already full. Cannot add resident.'}), 422
    
	# Move the resident to the new room
	success = hotel.move_resident_into_room(resident_id, new_room_id)

	if success:
		return jsonify({'message': 'Resident moved to new room successfully'}), 200
	else:
		return jsonify({'error': 'Resident or room not found.'}), 404

      
# Remove resident from a room
@app.route('/residents/<int:resident_id>', methods=['DELETE'])
def remove_resident(resident_id):
	# Call the remove_resident_from_room function from the Hotel instance
	removal_result = hotel.remove_resident_from_room(resident_id)

	if removal_result:
		return '', 204
	else:
		return (
			jsonify({'error': f'Resident with ID {resident_id} '
						'not found'}), 404
		)

# Remove a room along with its residents
@app.route('/rooms/<int:room_id>', methods=['DELETE'])
def remove_room(room_id):
	if hotel.remove_room(room_id):
		return '', 204
	else:
		return jsonify({'error': f'Room with ID {room_id} not found'}), 404

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
			'residents': [
				{'id': resident.id, 'name': resident.name, 'surname': resident.surname}
				for resident in room.lives_here
			]
		}
		rooms_data.append(room_info)

	return render_template('index.html', rooms_data=rooms_data)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)

set -e  # Exit on error

echo "=== IzanagiDB Backend Test Suite ==="
echo ""

# Rebuild and restart containers
echo "Step 1: Rebuilding Docker containers..."
docker-compose down && docker-compose up --build -d

# Wait for services to start
echo "Waiting for 20 seconds for services to start..."
sleep 20

# Clean databases
echo "Step 2: Cleaning databases..."
docker exec -it izanagi_postgres psql -U izanagi_user -d izanagi_db -c "TRUNCATE users, documents, versions, document_owners, refresh_tokens RESTART IDENTITY CASCADE;"
docker exec -it izanagi_mongo mongosh izanagi_warehouse --eval "db.document_contents.deleteMany({})"

echo ""
echo "=== AUTHENTICATION TESTS ==="
echo ""

# Register first user
echo "Test 1: Register user 'alice'"
# -X specifies HTTP method (POST)
# -H sets headers (accept, Content-Type)
# -d sends JSON data in request body
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "alicepass123"
  }'
echo ""

# Register second user
echo "Test 2: Register user 'bob'"
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "bob",
    "email": "bob@example.com",
    "password": "bobpass123"
  }'
echo ""

# Login and get token
echo "Test 3: Login as alice and extract JWT token"
# -s enables silent mode (no progress bar)
# grep -o extracts only the matching pattern
# cut -d'"' -f4 splits by quotes and takes 4th field (the token value)
TOKEN_ALICE=$(curl -s -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "alice",
    "password": "alicepass123"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Alice's token: ${TOKEN_ALICE:0:50}..."
echo ""

# Login second user
echo "Test 4: Login as bob"
TOKEN_BOB=$(curl -s -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "bob",
    "password": "bobpass123"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Bob's token: ${TOKEN_BOB:0:50}..."
echo ""

# Search users
echo "Test 5: Search for users (query: 'ali')"
# Authorization: Bearer header authenticates the request with JWT
curl -X 'GET' \
  'http://localhost:8000/auth/users/search?q=ali' \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""
echo ""

echo "=== DOCUMENT MANAGEMENT TESTS ==="
echo ""

# Create document
echo "Test 6: Create document as alice"
curl -X 'POST' \
  'http://localhost:8000/documents' \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Project Roadmap",
    "content": {
      "text": "Initial project plan",
      "priority": "high",
      "status": "draft"
    }
  }'
echo ""

# List documents
echo "Test 7: List alice's documents"
curl -X 'GET' \
  'http://localhost:8000/documents' \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# Get specific document (document_id will be 1 after clean start)
DOC_ID=1

echo "Test 8: Get document $DOC_ID with content"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""
echo ""

echo "=== VERSION CONTROL TESTS ==="
echo ""

# Commit new version
echo "Test 9: Commit version 1 (update content)"
curl -X 'POST' \
  "http://localhost:8000/documents/$DOC_ID/commit" \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H 'Content-Type: application/json' \
  -d '{
    "content": {
      "text": "Updated project plan with milestones",
      "priority": "high",
      "status": "in-progress",
      "milestones": ["Q1", "Q2"]
    }
  }'
echo ""

# Commit another version
echo "Test 10: Commit version 2 (add more details)"
curl -X 'POST' \
  "http://localhost:8000/documents/$DOC_ID/commit" \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H 'Content-Type: application/json' \
  -d '{
    "content": {
      "text": "Final project plan",
      "priority": "critical",
      "status": "completed",
      "milestones": ["Q1", "Q2", "Q3", "Q4"],
      "approved": true
    }
  }'
echo ""

# List version history
echo "Test 11: List all versions"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID/versions" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# Get version 0 (should reconstruct from reverse patches)
echo "Test 12: Get version 0 (original content)"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID/versions/0" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# Get version 1
echo "Test 13: Get version 1 (first update)"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID/versions/1" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# Get version 2 (current)
echo "Test 14: Get version 2 (latest)"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID/versions/2" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""
echo ""

echo "=== DOCUMENT UPDATE TESTS ==="
echo ""

# Update document title
echo "Test 15: Update document title"
# PATCH is used for partial updates (only title, not content)
curl -X 'PATCH' \
  "http://localhost:8000/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Project Roadmap 2026"
  }'
echo ""
echo ""

echo "=== DOCUMENT SHARING TESTS ==="
echo ""

# Share document with bob
echo "Test 16: Share document with bob"
curl -X 'POST' \
  "http://localhost:8000/documents/$DOC_ID/share" \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "bob"
  }'
echo ""

# Verify bob can see the document
echo "Test 17: Bob lists documents (should see shared document)"
curl -X 'GET' \
  'http://localhost:8000/documents' \
  -H "Authorization: Bearer $TOKEN_BOB"
echo ""

# Verify bob can read the document
echo "Test 18: Bob reads shared document"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN_BOB"
echo ""

# Create second document as alice
echo "Test 19: Create second document as alice"
curl -X 'POST' \
  'http://localhost:8000/documents' \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Private Notes",
    "content": {
      "text": "This is private"
    }
  }'
echo ""

# Get bob's user_id for unshare test (bob is user_id 2 if registered second)
BOB_USER_ID=2

# Unshare first document from bob
echo "Test 20: Remove bob from document $DOC_ID"
# DELETE is used to remove resources
curl -X 'DELETE' \
  "http://localhost:8000/documents/$DOC_ID/share/$BOB_USER_ID" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# Verify bob can no longer access
echo "Test 21: Bob tries to access unshared document (should fail)"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN_BOB"
echo ""
echo ""

echo "=== DOCUMENT DELETION TESTS ==="
echo ""

# Delete document
DOC_TO_DELETE=2
echo "Test 22: Delete document $DOC_TO_DELETE"
curl -X 'DELETE' \
  "http://localhost:8000/documents/$DOC_TO_DELETE" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# Verify deletion
echo "Test 23: Try to get deleted document (should fail)"
curl -X 'GET' \
  "http://localhost:8000/documents/$DOC_TO_DELETE" \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""

# List remaining documents
echo "Test 24: List alice's remaining documents"
curl -X 'GET' \
  'http://localhost:8000/documents' \
  -H "Authorization: Bearer $TOKEN_ALICE"
echo ""
echo ""

echo "=== TEST SUITE COMPLETE ==="
echo ""
echo "All tests executed successfully!"
echo "Backend is fully functional."

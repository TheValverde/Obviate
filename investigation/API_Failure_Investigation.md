# API Failure Investigation Plan

**Date:** August 24, 2025  
**Test Run:** Latest comprehensive API test  
**Total Failures:** 9 unique scenarios (inflated to 18 actual test failures due to multiple entity testing)

---

## 📋 Failed Tests Summary

### **Column Operations Failures (4 unique scenarios)**

| Endpoint | Method | Status | Error | Test Count | Unique Scenario |
|----------|--------|--------|-------|------------|-----------------|
| `/v1/columns/board/{id}` | GET | ❌ 500 | Internal server error | 1 | Column listing by board |
| `/v1/columns/{id}/reorder` | POST | ❌ 500 | Internal server error | 2 | Column reordering |
| `/v1/columns/{id}/reorder` | POST | ❌ 0 | Server disconnected | 1 | Column reordering (server crash) |
| `/v1/columns/{id}` | DELETE | ❌ 500 | Internal server error | 4 | Column deletion |

### **Card Operations Failures (5 unique scenarios)**

| Endpoint | Method | Status | Error | Test Count | Unique Scenario |
|----------|--------|--------|-------|------------|-----------------|
| `/v1/cards/{id}` | PUT | ❌ 500 | Internal server error | 4 | Card updates |
| `/v1/cards/{id}/move` | POST | ❌ 500 | Internal server error | 2 | Card movement between columns |
| `/v1/cards/{id}/reorder` | POST | ❌ 500 | Internal server error | 2 | Card reordering within columns |
| `/v1/cards/{id}` | DELETE | ❌ 500 | Internal server error | 4 | Card deletion |

---

## 🔍 Investigation Plan

### **Phase 1: Environment & Setup Verification**

#### **1.1 Server Health Check**
- [ ] Verify FastAPI server is running and stable
- [ ] Check server logs for any startup errors
- [ ] Verify database connection and health
- [ ] Check for any recent code changes that might affect these endpoints

#### **1.2 Database State Analysis**
- [ ] Verify database schema is up to date
- [ ] Check for any pending migrations
- [ ] Verify table structures match expected models
- [ ] Check for any data corruption or constraint violations

### **Phase 2: Individual Endpoint Investigation**

#### **2.1 Column Listing by Board (`GET /v1/columns/board/{id}`)**
**Priority:** Medium  
**Error:** 500 Internal Server Error

**Failed Test Code:**
```python
# Get columns by board ID
result = await self.make_request("GET", f"/v1/columns/board/{self.test_data['board_id']}")
self.results.append(result)
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test endpoint manually with valid board ID
   - [ ] Test with invalid board ID
   - [ ] Check response headers and body

2. **Code Review**
   - [ ] Locate the endpoint handler in the codebase
   - [ ] Review the query logic for column retrieval by board
   - [ ] Check for any missing error handling

3. **Database Query Analysis**
   - [ ] Verify the SQL query being generated
   - [ ] Check if the query executes successfully in database
   - [ ] Look for any foreign key constraint issues

4. **Log Analysis**
   - [ ] Check server logs for detailed error messages
   - [ ] Look for any stack traces or exception details

#### **2.2 Column Reordering (`POST /v1/columns/{id}/reorder`)**
**Priority:** High  
**Error:** 500 Internal Server Error + Server Disconnection

**Failed Test Code:**
```python
# Reorder columns
if len(self.test_data['column_ids']) >= 2:
    # Move first column to last position
    column_id = self.test_data['column_ids'][0]
    result = await self.make_request("POST", f"/v1/columns/{column_id}/reorder?new_position={len(self.test_data['column_ids']) - 1}")
    self.results.append(result)
    
    # Move it back to first position
    result = await self.make_request("POST", f"/v1/columns/{column_id}/reorder?new_position=0")
    self.results.append(result)
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test reordering with valid column ID and position
   - [ ] Test with invalid positions (negative, out of bounds)
   - [ ] Test with non-existent column ID

2. **Code Review**
   - [ ] Locate the reorder endpoint handler
   - [ ] Review the position calculation logic
   - [ ] Check for transaction handling and rollback logic

3. **Database Transaction Analysis**
   - [ ] Verify transaction isolation levels
   - [ ] Check for deadlock scenarios
   - [ ] Review position update logic

4. **Server Stability Investigation**
   - [ ] Check for memory leaks during reorder operations
   - [ ] Verify timeout settings
   - [ ] Look for any infinite loops or blocking operations

#### **2.3 Column Deletion (`DELETE /v1/columns/{id}`)**
**Priority:** High  
**Error:** 500 Internal Server Error

**Failed Test Code:**
```python
# Delete columns
for column_id in self.test_data['column_ids']:
    result = await self.make_request("DELETE", f"/v1/columns/{column_id}")
    self.results.append(result)
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test deletion of empty column
   - [ ] Test deletion of column with cards
   - [ ] Test deletion of non-existent column

2. **Code Review**
   - [ ] Locate the delete endpoint handler
   - [ ] Review cascade deletion logic
   - [ ] Check for foreign key constraint handling

3. **Database Constraint Analysis**
   - [ ] Verify foreign key relationships
   - [ ] Check for any circular references
   - [ ] Review cascade delete settings

4. **Data Integrity Check**
   - [ ] Verify no orphaned records after deletion attempts
   - [ ] Check for any constraint violations

#### **2.4 Card Updates (`PUT /v1/cards/{id}`)**
**Priority:** High  
**Error:** 500 Internal Server Error

**Failed Test Code:**
```python
# Update cards
for i, card_id in enumerate(self.test_data['card_ids']):
    if i < len(self.test_data['card_etags']) and self.test_data['card_etags'][i]:
        update_data = {
            "title": f"Updated {card_titles[i]}",
            "description": f"Updated description for {card_titles[i]}",
            "priority": min(5, priorities[i] + 1)
        }
        headers = {"If-Match": self.test_data['card_etags'][i]}
        result = await self.make_request("PUT", f"/v1/cards/{card_id}", 
                                       update_data, headers)
        self.results.append(result)
        
        if result.success and result.response_data:
            self.test_data['card_etags'][i] = result.response_data.get('etag')
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test updating card title and description
   - [ ] Test updating card priority
   - [ ] Test updating card labels and assignees
   - [ ] Test with invalid card ID

2. **Code Review**
   - [ ] Locate the update endpoint handler
   - [ ] Review validation logic for card updates
   - [ ] Check for optimistic concurrency handling

3. **Data Validation Analysis**
   - [ ] Verify all required fields are properly validated
   - [ ] Check for any type conversion issues
   - [ ] Review JSON parsing and serialization

4. **ETag Handling**
   - [ ] Verify ETag generation and validation
   - [ ] Check for any race conditions

#### **2.5 Card Movement (`POST /v1/cards/{id}/move`)**
**Priority:** High  
**Error:** 500 Internal Server Error

**Failed Test Code:**
```python
# Move cards between columns
if len(self.test_data['card_ids']) >= 2 and len(self.test_data['column_ids']) >= 2:
    card_id = self.test_data['card_ids'][0]
    target_column_id = self.test_data['column_ids'][1]
    result = await self.make_request("POST", f"/v1/cards/{card_id}/move?column_id={target_column_id}&position=0")
    self.results.append(result)
    
    # Move it back
    result = await self.make_request("POST", f"/v1/cards/{card_id}/move?column_id={self.test_data['column_ids'][0]}&position=0")
    self.results.append(result)
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test moving card between valid columns
   - [ ] Test moving to non-existent column
   - [ ] Test moving with invalid position values

2. **Code Review**
   - [ ] Locate the move endpoint handler
   - [ ] Review column validation logic
   - [ ] Check position calculation and reordering

3. **Business Logic Analysis**
   - [ ] Verify column exists and belongs to same board
   - [ ] Check for any workflow restrictions
   - [ ] Review position adjustment logic

#### **2.6 Card Reordering (`POST /v1/cards/{id}/reorder`)**
**Priority:** High  
**Error:** 500 Internal Server Error

**Failed Test Code:**
```python
# Reorder cards
if len(self.test_data['card_ids']) >= 2:
    card_id = self.test_data['card_ids'][0]
    result = await self.make_request("POST", f"/v1/cards/{card_id}/reorder?new_position={len(self.test_data['card_ids']) - 1}")
    self.results.append(result)
    
    # Move it back to first position
    result = await self.make_request("POST", f"/v1/cards/{card_id}/reorder?new_position=0")
    self.results.append(result)
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test reordering within same column
   - [ ] Test with invalid position values
   - [ ] Test with cards in different columns

2. **Code Review**
   - [ ] Locate the reorder endpoint handler
   - [ ] Review position calculation logic
   - [ ] Check for any boundary conditions

3. **Database Query Analysis**
   - [ ] Verify the position update queries
   - [ ] Check for any transaction issues
   - [ ] Review any triggers or constraints

#### **2.7 Card Deletion (`DELETE /v1/cards/{id}`)**
**Priority:** High  
**Error:** 500 Internal Server Error

**Failed Test Code:**
```python
# Delete cards
for card_id in self.test_data['card_ids']:
    result = await self.make_request("DELETE", f"/v1/cards/{card_id}")
    self.results.append(result)
```

**Investigation Steps:**
1. **Manual Testing**
   - [ ] Test deletion of existing card
   - [ ] Test deletion of non-existent card
   - [ ] Test deletion of card with dependencies

2. **Code Review**
   - [ ] Locate the delete endpoint handler
   - [ ] Review cascade deletion logic
   - [ ] Check for any soft delete implementation

3. **Dependency Analysis**
   - [ ] Check for any foreign key relationships
   - [ ] Verify no orphaned records
   - [ ] Review any audit trail requirements

### **Phase 3: Root Cause Analysis**

#### **3.1 Common Patterns Analysis**
- [ ] Identify common error patterns across all failures
- [ ] Look for shared code paths or dependencies
- [ ] Check for any recent changes that might affect multiple endpoints

#### **3.2 Database Connection Issues**
- [ ] Verify connection pool settings
- [ ] Check for connection timeouts
- [ ] Review transaction isolation levels

#### **3.3 Error Handling Review**
- [ ] Check if proper exception handling is in place
- [ ] Verify error responses are consistent
- [ ] Review logging configuration

### **Phase 4: Fix Implementation**

#### **4.1 Code Fixes**
- [ ] Implement proper error handling for each endpoint
- [ ] Add input validation where missing
- [ ] Fix any database query issues
- [ ] Add proper transaction handling

#### **4.2 Testing**
- [ ] Create unit tests for each fixed endpoint
- [ ] Run integration tests
- [ ] Verify fixes don't break existing functionality

#### **4.3 Documentation**
- [ ] Update API documentation
- [ ] Document any breaking changes
- [ ] Update error response schemas

---

## 🛠️ Tools and Commands

### **Manual Testing Commands**
```bash
# Test column listing by board
curl -X GET "http://localhost:8000/v1/columns/board/{board_id}"

# Test column reordering
curl -X POST "http://localhost:8000/v1/columns/{column_id}/reorder?new_position=1"

# Test card updates
curl -X PUT "http://localhost:8000/v1/cards/{card_id}" \
  -H "Content-Type: application/json" \
  -H "If-Match: {etag}" \
  -d '{"title": "Updated Title"}'
```

### **Database Investigation**
```sql
-- Check column data
SELECT * FROM columns WHERE board_id = '{board_id}';

-- Check card data
SELECT * FROM cards WHERE id = '{card_id}';

-- Check foreign key constraints
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY';
```

### **Server Log Analysis**
```bash
# Check FastAPI logs
docker-compose logs api

# Check database logs
docker-compose logs db
```

---

## 📊 Success Criteria

### **Phase 1 Success:**
- [ ] All environment issues identified and resolved
- [ ] Database state verified as healthy
- [ ] Server stability confirmed

### **Phase 2 Success:**
- [ ] Root cause identified for each failed endpoint
- [ ] Manual testing confirms the issues
- [ ] Code review completed for each endpoint

### **Phase 3 Success:**
- [ ] Common patterns identified
- [ ] Shared root causes documented
- [ ] Fix strategy defined

### **Phase 4 Success:**
- [ ] All endpoints return proper responses
- [ ] Error handling is consistent
- [ ] Test suite passes with 100% success rate

---

## 🚨 Emergency Procedures

### **If Server Becomes Unstable:**
1. Stop the test immediately
2. Check server logs for critical errors
3. Restart the FastAPI service
4. Verify database integrity

### **If Database Issues Found:**
1. Backup current data
2. Check for any pending migrations
3. Verify schema consistency
4. Consider database reset if necessary

---

**Next Steps:** Begin with Phase 1 - Environment & Setup Verification

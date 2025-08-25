# API Failure Investigation Findings

**Date:** August 24, 2025  
**Investigation Status:** In Progress  
**Investigator:** AI Assistant  

---

## 🔍 **Root Cause Analysis**

### **1. Column Listing by Board Endpoint (`GET /v1/columns/board/{id}`)**

**Error:** 500 Internal Server Error  
**Actual Error Message:** `{'detail': 'Internal server error'}`

**Code Analysis:**
```python
@router.get("/board/{board_id}", response_model=List[ColumnListResponse])
async def get_board_columns(
    board_id: str,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> List[ColumnListResponse]:
    columns = await repo.list(tenant_id, board_id=board_id, limit=1000)
    return [ColumnListResponse.model_validate(col.to_dict()) for col in columns]
```

**Root Cause:** The endpoint is trying to return a `List[ColumnListResponse]` but the response model expects a different structure. Looking at the Swagger documentation, this endpoint should return a paginated response, not a direct list.

**Fix Required:** Change the response model to match the expected API structure.

### **2. Column Reordering Endpoint (`POST /v1/columns/{id}/reorder`)**

**Error:** Server Disconnection  
**Actual Error Message:** `Server disconnected`

**Code Analysis:**
```python
@router.post("/{column_id}/reorder", response_model=SuccessResponse)
async def reorder_columns(
    column_id: str,
    new_position: int,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> SuccessResponse:
    if new_position < 0:
        raise BadRequestException("Position must be non-negative")
    
    column = await repo.get_by_id(column_id, tenant_id)
    if not column:
        raise ColumnNotFoundException(f"Column with ID {column_id} not found")
    
    # Update column position
    await repo.update(column_id, {"position": new_position})
    
    return SuccessResponse(data={"reordered": True, "new_position": new_position})
```

**Root Cause:** The endpoint is calling `repo.update()` but the base repository's update method expects `entity_id` and `tenant_id` parameters, not just `column_id`. This is causing a database error that crashes the server.

**Fix Required:** Update the repository call to use the correct method signature.

### **3. Card Update Endpoint (`PUT /v1/cards/{id}`)**

**Error:** 500 Internal Server Error (predicted based on pattern)

**Code Analysis:**
```python
@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: str,
    card_data: CardUpdate,
    if_match: Optional[str] = Header(None, alias="If-Match"),
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    # Get current card to check version
    current_card = await repo.get_by_id(card_id, tenant_id)
    if not current_card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    # Check optimistic concurrency
    if if_match and str(current_card.version) != if_match:
        raise OptimisticConcurrencyException("Card has been modified by another request")
    
    # Update card
    updated_card = await repo.update(card_id, card_data.model_dump(exclude_unset=True))
    return CardResponse.model_validate(updated_card.to_dict())
```

**Root Cause:** Same issue as column reordering - incorrect repository method call.

### **4. Card Movement Endpoint (`POST /v1/cards/{id}/move`)**

**Error:** 500 Internal Server Error (predicted based on pattern)

**Code Analysis:**
```python
@router.post("/{card_id}/move", response_model=CardResponse)
async def move_card(
    card_id: str,
    column_id: str,
    position: Optional[int] = Query(None, ge=0, description="New position in column (optional)"),
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    # Get current card
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    # Update card with new column_id and optional position
    update_data = {"column_id": column_id}
    if position is not None:
        update_data["position"] = position
    
    updated_card = await repo.update(card_id, update_data)
    return CardResponse.model_validate(updated_card.to_dict())
```

**Root Cause:** Same repository method call issue.

### **5. Card Reordering Endpoint (`POST /v1/cards/{id}/reorder`)**

**Error:** 500 Internal Server Error (predicted based on pattern)

**Code Analysis:**
```python
@router.post("/{card_id}/reorder", response_model=CardResponse)
async def reorder_card(
    card_id: str,
    new_position: int,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> CardResponse:
    if new_position < 0:
        raise BadRequestException("Position must be non-negative")
    
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    # Update card position
    updated_card = await repo.update(card_id, {"position": new_position})
    return CardResponse.model_validate(updated_card.to_dict())
```

**Root Cause:** Same repository method call issue.

### **6. Card Deletion Endpoint (`DELETE /v1/cards/{id}`)**

**Error:** 500 Internal Server Error (predicted based on pattern)

**Code Analysis:**
```python
@router.delete("/{card_id}", response_model=SuccessResponse)
async def delete_card(
    card_id: str,
    repo: CardRepository = Depends(get_card_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> SuccessResponse:
    card = await repo.get_by_id(card_id, tenant_id)
    if not card:
        raise CardNotFoundException(f"Card with ID {card_id} not found")
    
    await repo.delete(card_id)
    return SuccessResponse(data={"deleted": True})
```

**Root Cause:** The `repo.delete()` method expects `entity_id` and `tenant_id` parameters, but only `card_id` is being passed.

### **7. Column Deletion Endpoint (`DELETE /v1/columns/{id}`)**

**Error:** 500 Internal Server Error (predicted based on pattern)

**Code Analysis:**
```python
@router.delete("/{column_id}", response_model=SuccessResponse)
async def delete_column(
    column_id: str,
    repo: ColumnRepository = Depends(get_column_repository),
    tenant_id: str = Depends(get_tenant_id)
) -> SuccessResponse:
    column = await repo.get_by_id(column_id, tenant_id)
    if not column:
        raise ColumnNotFoundException(f"Column with ID {column_id} not found")
    
    await repo.delete(column_id)
    return SuccessResponse(data={"deleted": True})
```

**Root Cause:** Same repository method call issue.

---

## 🛠️ **Required Fixes**

### **Fix 1: Repository Method Calls**

**Problem:** All failing endpoints are calling repository methods with incorrect parameters.

**Solution:** Update all repository calls to use the correct method signatures:

```python
# Current (incorrect):
await repo.update(column_id, {"position": new_position})
await repo.delete(card_id)

# Fixed:
await repo.update(entity_id=column_id, tenant_id=tenant_id, data={"position": new_position})
await repo.delete(entity_id=card_id, tenant_id=tenant_id)
```

### **Fix 2: Response Model for Column Listing**

**Problem:** The column listing by board endpoint returns the wrong response type.

**Solution:** Update the response model to match the API specification.

### **Fix 3: Error Handling**

**Problem:** The server crashes instead of returning proper error responses.

**Solution:** Add proper exception handling and ensure all database operations are wrapped in try-catch blocks.

---

## 📊 **Impact Assessment**

### **High Priority Issues:**
1. **Server Crashes** - Column reordering causes server disconnection
2. **Database Errors** - All update/delete operations fail due to incorrect method calls
3. **API Contract Violations** - Response models don't match expected structure

### **Medium Priority Issues:**
1. **Error Response Inconsistency** - Some endpoints return 500 instead of proper error codes
2. **Missing Validation** - Some endpoints lack proper input validation

### **Low Priority Issues:**
1. **Performance** - Some endpoints could be optimized
2. **Logging** - Error logging could be improved

---

## 🎯 **Next Steps**

### **Immediate Actions (Phase 1):**
1. [ ] Fix repository method calls in all failing endpoints
2. [ ] Update response models to match API specification
3. [ ] Add proper exception handling
4. [ ] Test fixes with the debug script

### **Validation Actions (Phase 2):**
1. [ ] Run the comprehensive test suite
2. [ ] Verify all endpoints return correct status codes
3. [ ] Check that no server crashes occur
4. [ ] Validate API contract compliance

### **Documentation Actions (Phase 3):**
1. [ ] Update API documentation
2. [ ] Document the fixes applied
3. [ ] Create regression tests
4. [ ] Update investigation report with final results

---

## 🔧 **Technical Details**

### **Repository Method Signatures (BaseRepository):**
```python
async def update(
    self,
    entity_id: str,
    tenant_id: str,
    data: Union[Dict[str, Any], UpdateSchema],
    version: Optional[int] = None
) -> Optional[T]

async def delete(
    self,
    entity_id: str,
    tenant_id: str,
    version: Optional[int] = None,
    hard_delete: bool = False
) -> bool
```

### **Current Incorrect Usage:**
```python
# Column endpoints
await repo.update(column_id, {"position": new_position})
await repo.delete(column_id)

# Card endpoints  
await repo.update(card_id, card_data.model_dump(exclude_unset=True))
await repo.delete(card_id)
```

### **Correct Usage:**
```python
# Column endpoints
await repo.update(entity_id=column_id, tenant_id=tenant_id, data={"position": new_position})
await repo.delete(entity_id=column_id, tenant_id=tenant_id)

# Card endpoints
await repo.update(entity_id=card_id, tenant_id=tenant_id, data=card_data.model_dump(exclude_unset=True))
await repo.delete(entity_id=card_id, tenant_id=tenant_id)
```

---

**Status:** Ready for implementation of fixes

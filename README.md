# Camp-DeepSeek


## First Sprint Selection Criteria

For Sprint 1, we should select requirements that:
1. **Establish the core foundation** of the system
2. **Provide immediate value** to users
3. **Are technically feasible** within 2-4 weeks
4. **Have minimal dependencies** on other features
5. **Demonstrate the architecture** working end-to-end




### Initial Build and Test

```bash
# Build and start all services
docker-compose up --build -d


#  Test backend API
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

curl http://localhost:8000/
# Expected: {"message":"Camp Management System API","version":"1.0.0"}

```
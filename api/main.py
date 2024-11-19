from fastapi import FastAPI
import router # assuming this is the file where your router is defined

app = FastAPI()

# Include the item router
app.include_router(router.router)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from get_3_point import RouteCalculator, calculate_points_G_n_T
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Route Evaluation API",
    description="API để tính toán và đánh giá khoảng cách, thời gian giữa 3 địa điểm",
    version="1.0.0"
)

# Request model
class LocationRequest(BaseModel):
    work_address: str
    home_address: str
    gym_address: str
    api_key: str = None  # Optional, sẽ dùng từ env nếu không có
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_address": "Đại học Thương Mại, Hà Nội",
                "home_address": "Công viên Cầu Giấy, Hà Nội",
                "gym_address": "Bến xe Mỹ Đình, Hà Nội",
                "api_key": "your_goong_api_key"
            }
        }

# Response model
class EvaluationResponse(BaseModel):
    evaluation: float
    G: float
    T: float
    dRate: float
    tRate: float
    distances: dict
    times: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluation": 4.22,
                "G": 4.11,
                "T": 4.42,
                "dRate": 0.82,
                "tRate": 0.88,
                "distances": {
                    "work_home": 1.5,
                    "home_gym": 2.3,
                    "work_gym": 3.2
                },
                "times": {
                    "work_home": 8.5,
                    "home_gym": 12.3,
                    "work_gym": 18.5
                }
            }
        }

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Route Evaluation API is running",
        "endpoints": {
            "POST /evaluate": "Đánh giá vị trí nhà giữa công ty và phòng gym"
        }
    }

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate_location(request: LocationRequest):
    """
    Đánh giá vị trí nhà dựa trên khoảng cách và thời gian từ công ty và phòng gym.
    
    - **work_address**: Địa chỉ công ty
    - **home_address**: Địa chỉ nhà
    - **gym_address**: Địa chỉ phòng gym
    - **api_key**: Goong Maps API key (optional, sẽ dùng từ env nếu không có)
    
    Returns:
    - **evaluation**: Điểm đánh giá tổng (0-5)
    - **G**: Điểm dựa trên khoảng cách (0-5)
    - **T**: Điểm dựa trên thời gian (0-5)
    - **dRate**: Tỷ lệ khoảng cách
    - **tRate**: Tỷ lệ thời gian
    - **distances**: Các khoảng cách (km)
    - **times**: Các thời gian (phút)
    """
    try:
        # Get API key
        api_key = request.api_key or os.getenv('GOONG_API_KEY')
        
        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="API key is required. Provide it in request body or set GOONG_API_KEY environment variable."
            )
        
        # Initialize calculator
        calculator = RouteCalculator(api_key)
        
        # Get distances and times
        dis_workhome, time_workhome, dis_homegym, time_homegym, dis_workgym, time_workgym = \
            calculator.get_location_n_time(
                request.work_address,
                request.home_address,
                request.gym_address
            )
        
        # Check if geocoding was successful
        if dis_workhome is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to geocode one or more addresses. Please check the addresses."
            )
        
        # Calculate evaluation
        evaluation, G, T, dRate, tRate = calculate_points_G_n_T(
            dis_workhome, time_workhome,
            dis_homegym, time_homegym,
            dis_workgym, time_workgym
        )
        
        # Prepare response
        return EvaluationResponse(
            evaluation=round(evaluation, 2),
            G=round(G, 2),
            T=round(T, 2),
            dRate=round(dRate, 4),
            tRate=round(tRate, 4),
            distances={
                "work_home": dis_workhome,
                "home_gym": dis_homegym,
                "work_gym": dis_workgym
            },
            times={
                "work_home": time_workhome,
                "home_gym": time_homegym,
                "work_gym": time_workgym
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

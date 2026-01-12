from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
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

# Get default max_scale from environment variable
DEFAULT_MAX_SCALE = int(os.getenv('MAX_SCALE', '5'))

# Response model
class EvaluationResponse(BaseModel):
    rating: float
    G: float
    T: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "rating": 4.22,
                "G": 4.11,
                "T": 4.42
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
def evaluate_location(
    work_address: str = Form(..., description="Địa chỉ công ty"),
    home_address: str = Form(..., description="Địa chỉ nhà"),
    gym_address: str = Form(..., description="Địa chỉ phòng gym"),
    api_key: Optional[str] = Form(None, description="Goong Maps API key (optional)"),
    max_scale: int = Form(DEFAULT_MAX_SCALE, description="Thang điểm tối đa")
):
    """
    Đánh giá vị trí nhà dựa trên khoảng cách và thời gian từ công ty và phòng gym.
    
    - **work_address**: Địa chỉ công ty
    - **home_address**: Địa chỉ nhà
    - **gym_address**: Địa chỉ phòng gym
    - **api_key**: Goong Maps API key (optional, sẽ dùng từ env nếu không có)
    
    Returns:
    - **rating**: Điểm đánh giá tổng (0-5)
    - **G**: Điểm dựa trên khoảng cách (0-5)
    - **T**: Điểm dựa trên thời gian (0-5)
    - **dRate**: Tỷ lệ khoảng cách
    - **tRate**: Tỷ lệ thời gian
    - **distances**: Các khoảng cách (km)
    - **times**: Các thời gian (phút)
    """
    try:
        # Get API key
        used_api_key = api_key or os.getenv('GOONG_API_KEY')
        
        if not used_api_key:
            raise HTTPException(
                status_code=400,
                detail="API key is required. Provide it in request body or set GOONG_API_KEY environment variable."
            )
        
        # Initialize calculator
        calculator = RouteCalculator(used_api_key)
        
        # Get distances and times
        dis_workhome, time_workhome, dis_homegym, time_homegym, dis_workgym, time_workgym = \
            calculator.get_location_n_time(
                work_address,
                home_address,
                gym_address
            )
        
        # Check if geocoding was successful
        if dis_workhome is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to geocode one or more addresses. Please check the addresses."
            )
        
        # Calculate rating
        rating, G, T, dRate, tRate = calculate_points_G_n_T(
            dis_workhome, time_workhome,
            dis_homegym, time_homegym,
            dis_workgym, time_workgym,
            max_scale=max_scale
        )
        
        # Prepare response
        return EvaluationResponse(
            rating=round(rating, 2),
            G=round(G, 2),
            T=round(T, 2)
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
    uvicorn.run(app, host="0.0.0.0", port=8452)

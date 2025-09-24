from fastapi import APIRouter, Depends, HTTPException
from app.services.firebase_service import FirebaseService
from datetime import datetime, timedelta
import random
from typing import List, Optional

router = APIRouter()

def generate_mock_payroll_data(farmer_id: str, month: str, farmer_name: str = "Unknown"):
    """Generate mock payroll data for a farmer"""
    year, month_num = month.split('-')
    
    # Mock attendance data
    attendance_days = random.randint(18, 22)  # 18-22 working days
    total_hours = attendance_days * random.uniform(7.5, 8.5)
    overtime_hours = max(0, total_hours - (attendance_days * 8))
    
    # Base calculations
    daily_rate = random.randint(200000, 300000)  # 200k-300k VND per day
    base_salary = daily_rate * attendance_days
    
    # Bonuses
    productivity_bonus = random.randint(0, 800000)  # Up to 800k VND
    quality_bonus = random.randint(0, 500000)      # Up to 500k VND
    overtime_pay = overtime_hours * (daily_rate / 8) * 1.5
    
    # Deductions
    social_insurance = base_salary * 0.08  # 8% social insurance
    health_insurance = base_salary * 0.015  # 1.5% health insurance
    advance_payment = random.randint(0, 1000000)  # Advance payments
    
    total_deductions = social_insurance + health_insurance + advance_payment
    total_gross = base_salary + productivity_bonus + quality_bonus + overtime_pay
    net_pay = total_gross - total_deductions
    
    return {
        "payroll_id": f"pay_{year}_{month_num}_{farmer_id}",
        "farmer_id": farmer_id,
        "farmer_name": farmer_name,
        "period": month,
        "attendance_days": attendance_days,
        "total_hours": round(total_hours, 1),
        "overtime_hours": round(overtime_hours, 1),
        "base_salary": int(base_salary),
        "daily_rate": daily_rate,
        "productivity_bonus": productivity_bonus,
        "quality_bonus": quality_bonus,
        "overtime_pay": int(overtime_pay),
        "gross_pay": int(total_gross),
        "deductions": {
            "social_insurance": int(social_insurance),
            "health_insurance": int(health_insurance),
            "advance_payment": advance_payment,
            "total": int(total_deductions)
        },
        "net_pay": int(net_pay),
        "payment_status": random.choice(["pending", "paid", "processing"]),
        "payment_date": None if random.choice([True, False]) else f"{year}-{month_num}-28",
        "payment_method": "bank_transfer",
        "bank_details": {
            "bank": "Vietcombank",
            "account": f"****{random.randint(1000, 9999)}"
        },
        "performance_metrics": {
            "attendance_rate": round((attendance_days / 22) * 100, 1),
            "productivity_score": random.randint(70, 95),
            "quality_score": random.randint(75, 98),
            "overtime_ratio": round((overtime_hours / total_hours) * 100, 1)
        },
        "notes": random.choice([
            "Excellent performance this month",
            "Regular attendance, good quality work",
            "Improvement needed in productivity",
            "Outstanding quality standards maintained",
            ""
        ])
    }

@router.get("/payroll/{farmer_id}/{month}")
async def get_farmer_payroll(
    farmer_id: str,
    month: str,  # Format: YYYY-MM
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get payroll details for a specific farmer and month"""
    try:
        # Get farmer info
        farmer = await firebase.get_document("farmers", farmer_id)
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
        
        farmer_name = farmer.get("full_name") or farmer.get("name") or "Unknown"
        
        # Generate mock payroll data
        payroll_data = generate_mock_payroll_data(farmer_id, month, farmer_name)
        
        return payroll_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payroll/farm/{farm_id}/{month}")
async def get_farm_payroll(
    farm_id: str,
    month: str,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get payroll summary for all farmers in a farm for a specific month"""
    try:
        # Get all farmers in the farm
        farmers = await firebase.query_documents(
            "farmers",
            filters=[("farm_id", "==", farm_id)]
        )
        
        if not farmers:
            return {"farm_id": farm_id, "month": month, "payrolls": [], "summary": {}}
        
        payrolls = []
        total_gross = 0
        total_deductions = 0
        total_net = 0
        
        for farmer in farmers:
            farmer_id = farmer["id"]
            farmer_name = farmer.get("full_name") or farmer.get("name") or "Unknown"
            
            payroll = generate_mock_payroll_data(farmer_id, month, farmer_name)
            payrolls.append(payroll)
            
            total_gross += payroll["gross_pay"]
            total_deductions += payroll["deductions"]["total"]
            total_net += payroll["net_pay"]
        
        summary = {
            "total_farmers": len(farmers),
            "total_gross_pay": total_gross,
            "total_deductions": total_deductions,
            "total_net_pay": total_net,
            "average_net_pay": int(total_net / len(farmers)) if farmers else 0,
            "payment_status_breakdown": {
                "paid": len([p for p in payrolls if p["payment_status"] == "paid"]),
                "pending": len([p for p in payrolls if p["payment_status"] == "pending"]),
                "processing": len([p for p in payrolls if p["payment_status"] == "processing"])
            }
        }
        
        return {
            "farm_id": farm_id,
            "month": month,
            "payrolls": payrolls,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payroll/calculate")
async def calculate_payroll(
    month: str,
    farm_id: Optional[str] = None,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Calculate payroll for all farmers or specific farm for a month"""
    try:
        # Get farmers
        if farm_id:
            farmers = await firebase.query_documents(
                "farmers",
                filters=[("farm_id", "==", farm_id)]
            )
        else:
            farmers = await firebase.query_documents("farmers")
        
        calculated_payrolls = []
        
        for farmer in farmers:
            farmer_id = farmer["id"]
            farmer_name = farmer.get("full_name") or farmer.get("name") or "Unknown"
            
            # In real implementation, this would calculate based on actual attendance
            payroll = generate_mock_payroll_data(farmer_id, month, farmer_name)
            
            # Save to database (mock)
            # await firebase.save_document("payrolls", payroll["payroll_id"], payroll)
            
            calculated_payrolls.append(payroll)
        
        return {
            "status": "success",
            "message": f"Calculated payroll for {len(calculated_payrolls)} farmers",
            "month": month,
            "farm_id": farm_id,
            "total_amount": sum(p["net_pay"] for p in calculated_payrolls),
            "payrolls": calculated_payrolls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payroll/summary/{month}")
async def get_payroll_summary(
    month: str,
    farm_id: Optional[str] = None,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Get overall payroll summary for a month"""
    try:
        # Get farmers
        if farm_id:
            farmers = await firebase.query_documents(
                "farmers",
                filters=[("farm_id", "==", farm_id)]
            )
        else:
            farmers = await firebase.query_documents("farmers")
        
        if not farmers:
            return {
                "month": month,
                "farm_id": farm_id,
                "summary": {"total_farmers": 0, "total_payroll": 0}
            }
        
        # Generate payroll data for summary
        total_gross = 0
        total_deductions = 0
        total_net = 0
        payment_status_count = {"paid": 0, "pending": 0, "processing": 0}
        performance_metrics = {"attendance": [], "productivity": [], "quality": []}
        
        for farmer in farmers:
            farmer_id = farmer["id"]
            farmer_name = farmer.get("full_name") or farmer.get("name") or "Unknown"
            
            payroll = generate_mock_payroll_data(farmer_id, month, farmer_name)
            
            total_gross += payroll["gross_pay"]
            total_deductions += payroll["deductions"]["total"]
            total_net += payroll["net_pay"]
            payment_status_count[payroll["payment_status"]] += 1
            
            performance_metrics["attendance"].append(payroll["performance_metrics"]["attendance_rate"])
            performance_metrics["productivity"].append(payroll["performance_metrics"]["productivity_score"])
            performance_metrics["quality"].append(payroll["performance_metrics"]["quality_score"])
        
        avg_attendance = sum(performance_metrics["attendance"]) / len(farmers)
        avg_productivity = sum(performance_metrics["productivity"]) / len(farmers)
        avg_quality = sum(performance_metrics["quality"]) / len(farmers)
        
        return {
            "month": month,
            "farm_id": farm_id,
            "summary": {
                "total_farmers": len(farmers),
                "total_gross_payroll": total_gross,
                "total_deductions": total_deductions,
                "total_net_payroll": total_net,
                "average_net_pay": int(total_net / len(farmers)),
                "payment_status": payment_status_count,
                "performance_averages": {
                    "attendance_rate": round(avg_attendance, 1),
                    "productivity_score": round(avg_productivity, 1),
                    "quality_score": round(avg_quality, 1)
                },
                "cost_breakdown": {
                    "base_salaries": int(total_gross * 0.75),  # Estimated breakdown
                    "bonuses": int(total_gross * 0.15),
                    "overtime": int(total_gross * 0.10),
                    "social_benefits": int(total_deductions * 0.70),
                    "advances": int(total_deductions * 0.30)
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payroll/{payroll_id}/pay")
async def process_payment(
    payroll_id: str,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Mark payroll as paid"""
    try:
        # In real implementation, integrate with payment gateway
        # For now, just return success
        
        return {
            "status": "success",
            "message": f"Payment processed for payroll {payroll_id}",
            "payroll_id": payroll_id,
            "payment_date": datetime.now().strftime("%Y-%m-%d"),
            "transaction_id": f"TXN_{random.randint(100000, 999999)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payroll/export/{month}")
async def export_payroll(
    month: str,
    format: str = "excel",  # excel, pdf, csv
    farm_id: Optional[str] = None,
    firebase: FirebaseService = Depends(FirebaseService)
):
    """Export payroll data"""
    try:
        # In real implementation, generate actual files
        # For now, return mock export info
        
        return {
            "status": "success",
            "message": f"Payroll export generated for {month}",
            "format": format,
            "farm_id": farm_id,
            "download_url": f"/downloads/payroll_{month}_{farm_id or 'all'}.{format}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "file_size": f"{random.randint(50, 500)}KB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
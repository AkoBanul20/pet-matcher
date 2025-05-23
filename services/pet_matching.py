import json
import requests 
from utilities.redis import RedisHelper
from extractor.pet_matcher import PetMatcher
from utilities.email import send_email

from utilities.constants import QUEUE_NAME, NOTIFICATION_QUEUE, PET_MATCHER_QUEUE

class PetMatchingService(object):
    def __init__(self, payload:str):
        self.payload                = json.loads(payload)
        self.redis                  = RedisHelper()
        self.redis_connection       = self.redis.redis_connection()
        self.run()

    def run(self):
        if QUEUE_NAME == "PET_MATCHER":
            self. pet_matching_image()
        elif QUEUE_NAME == "NOTIFICATION_REPORT":
            self.pet_report_notif_send()

    def pet_report_notif_send(self):
        try:
            payload = self.payload.get("payload")
            
            if not payload:
                queue_type = self.payload.get("queue_type", None)
                if queue_type:
                    if queue_type == "transfer_notification":
                        self.transaction_coordination_notif_send(self.payload)
                    else:
                        self.adoption_screening_notif_send(self.payload)
                    return
            owner = payload.get("owner_details")
            owner_email = owner.get("email")
            print(owner_email)
            owner_username = owner.get("username")
            _reported_image_url = payload.get("report_image_url")
            report_id = payload.get("report_id")
            reported_image_url = f"https://qcacac.site/api{_reported_image_url}"
            print(reported_image_url)
            subject = f"Report for your Lost Pet Post"
            body = f"""
            ""
            <html>
                <body>
                    <h2>We Found a Potential Match for Your Lost Pet</h2>
                    <p>Dear {owner_username},</p>
                    <p>We have identified a report that might match your lost pet. Please review the details below:</p>
                    <ul>
                        <li><strong>Report ID:</strong> {report_id}</li>
                        <li><strong>Reported Pet Image:</strong></li>
                    </ul>
                    <p><img src="{reported_image_url}" alt="Reported Pet Image" style="max-width: 300px; height: auto;"></p>
                    <p>If this is your pet, please contact the reporter or take the necessary steps to reclaim your pet.</p>
                    <p>Thank you for using our service!</p>


                    <p>Don't reply on this email. This a system generated email</p>
                </body>
            </html>
                    """
            
            print("sending email....")

            send_email(to_email=owner_email, subject=subject, body=body)
        except BaseException as e:
            print(f"Error in sending of report notification :{e}")

        return
    
    def transaction_coordination_notif_send(self, payload: dict):
        try:
            email = payload.get("email")
            name = payload.get("name")
            subject = f"Status of requested Transfer Coordination"
            request_data = payload.get("request_data")
            body = f"""
            <html>
                <body>
                    <h2>You're request is been approved!</h2>
                    <p>Dear Mr./Mrs. {name},</p>
                    <p>We are pleased to inform you that your transfer coordinaton request has been approved.:</p>
                    <ul>
                        <li><strong>Barangay/Name:</strong>  {request_data.get('barangay_name')} </li>
                        <li><strong>Address:</strong>  {request_data.get('address')} </li>
                        <li><strong>Pet Type:</strong>  {request_data.get('pet_type')} </li>
                        <li><strong>Requested Date:</strong>  {request_data.get('requested_date')} </li>
                    </ul>
                    <p>Please bring a QC ID or any valid ID. Thank you for using our service!</p>
                    <p>Don't reply on this email. This a system generated email</p>
                </body>
            </html>
            """
            print("sending email....")
            send_email(to_email=email, subject=subject, body=body)
        except BaseException as e:
            print("Error in sending transaction coordination")
    
    def adoption_screening_notif_send(self, payload: dict):
        try:
            pet_image_url = f"https://qcacac.site/api{payload.get('pet_image_url')}"
            schedule = payload.get("schedule")
            pet_name = payload.get("pet_name")
            # found_in = payload.get("found_in")
            # additional_details = payload.get("additional_details")
            email = payload.get("email")
            subject =f"Schedule of Screening for Your Adoption Request"
            body = f"""
            ""
            <html>
                <body>
                    <h2>Schedule of Screening for Your Adoption Request</h2>
                    <p>Dear Soon-to-be Fur Parent,</p>
                    <p>We are pleased to inform you that your adoption request has been scheduled for screening.:</p>
                    <ul>
                        <li><strong>Pet Name:</strong> {pet_name}</li>
                        <li><strong>When:</strong> {schedule}</li>
                        <li><strong>Where:</strong>Clemente St., Lupang Pangako, Payatas, Quezon City, Philippines</li>
                    </ul>
                    <p><img src="{pet_image_url}" alt="Pet Image" style="max-width: 300px; height: auto;"></p>
                    <p>Please bring a QC ID or any valid ID. Thank you for using our service!</p>
                    <p>Don't reply on this email. This a system generated email</p>
                </body>
            </html>
                    """
                
            print("sending email....")
            send_email(to_email=email, subject=subject, body=body)
        except BaseException as e:
            print(f"Error in sending of screening schedule :{e}")

        return


    def pet_matching_image(self):
        try:
            matcher = PetMatcher()
            lost_pet =  (self.payload.get("pet_image_url"))
            reported_pet = self.payload.get("report_image_url")

            result = matcher.compare_pet_images(
                lost_pet_image_path=lost_pet.lstrip("/"),
                reported_image_path=reported_pet.lstrip("/"),
                )
            
            try:
                print(f"Match probability: {result['similarity_score']:.2f}")
                print(f"Is match: {result['is_match']}")
                print(f"Confidence: {result['confidence']}%")
            except BaseException as e:
                print("error in getting the results data")
            
            redis_result_data = {
                "result": result,
                "payload": self.payload,
            }

            # if result['is_match']:

            self.redis_connection.sadd(NOTIFICATION_QUEUE,json.dumps(redis_result_data))
            # add update api status here

            report_id = self.payload.get("report_id")
            if report_id:
                self.status_matching_api_update(report_id, True)

            print("Successfully added to the queue")
        except BaseException as e:
            print(f"Error in pet matching.... {e}")
            self.redis_connection.sadd(PET_MATCHER_QUEUE, json.dumps(self.payload))
        return
        
    def status_matching_api_update(self, report_id: int, is_matched: bool = True):
        try:
            url = f"https://qcacac.site/api/v1/lost-pet-report/{report_id}/match"
            # url = f"http://127.0.0.1:8000/v1/lost-pet-report/{report_id}/match"
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                'is_matched': is_matched
            }

            response = requests.patch(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"Successfully updated match status for report {report_id}")
                return True
            else:
                print(f"Failed to update match status. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error updating match status: {e}")
            return False




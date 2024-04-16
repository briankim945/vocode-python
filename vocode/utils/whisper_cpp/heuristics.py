import re
import string
import json
from fuzzysearch import find_near_matches

from . import mappings


def check_regex(voice_input, phrase, errors_allowed=4):
    # shorter string goes first
    # print("START REGEX")
    # The smaller string is expected to be second.
    # For example
    # a = "hello"
    # b = "hello world"
    # check_regex(a, b) will return False
    # check_regex(b, a) will return True
    if len(voice_input) == 0 or len(phrase) == 0:
        return False
    test1 = voice_input.strip().replace(" ", "")
    if len(test1) == 0:
        return False
    try:
        regex_result = find_near_matches(
            phrase, voice_input, max_l_dist=errors_allowed)
        if len(regex_result) > 0:
            print(f"REGEX CHECK: {voice_input} and {phrase}")
            return True
        else:
            return False
    except ValueError:
        print("ValueError: check_regex substring match")
        return False


def enter_heuristics(voice_input_punc, input_data, full_prompt_row):
    if input_data is None or full_prompt_row is None:
        if 'press one' in voice_input.lower() or 'press 1' in voice_input.lower():
            return {"response": "1", "to_say": False}
        else:
            return {}
        
    voice_input_tmp = voice_input_punc.lower().translate(
        str.maketrans('', '', string.punctuation))
    voice_input = re.sub(r'\s+', ' ', voice_input_tmp)
    input_data_dict = json.loads(input_data)
    # These are hueristics for all calls
    heuristic_result = general_heuristics(voice_input, input_data_dict)
    # If we have a verbal/press response, return it
    # If not, continue to the more general heuristics
    if "response" in heuristic_result and heuristic_result["response"] is not None:
        return heuristic_result
    if full_prompt_row['call_type'] == 'eligibility':
        if full_prompt_row['phone_number'] == '+13237287232' or full_prompt_row['phone_number'] == '+18885172247':
            # Alignment Healthcare
            # +13237287232 is the general number. The first question is 'member or provider', when provider is clicked, it goes to the provider line.
            # +18885172247 is the provider line.
            heuristic_result = alignment_health_care_eligibility_heuristics(
                voice_input, input_data_dict)
            if "response" in heuristic_result:
                return heuristic_result
        elif full_prompt_row['phone_number'] == '+14155477800':
            # San Francisco Health Plan
            if check_regex(
                    voice_input,
                    "if you are a health care provider press five to apply for health insurance or return to your coverage press six months to reach a staff member or the operator"):
                return {"response": "5", "to_say": False}
            elif check_regex(voice_input, "to check eligibility using our automated system press one for pharmacy press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if you are a health care provider press five to apply for health insurance or return to your coverage"):
                return {"response": "5", "to_say": False}
            elif check_regex(voice_input, "if you are a health care provider press five to apply for health insurance or to renew your coverage"):
                return {"response": "5", "to_say": False}
            elif check_regex(voice_input, "if you are a health care provider press five to apply for health insurance or to renew your coverage press six to a staff"):
                return {"response": "5", "to_say": False}
            elif voice_input == "welcome to the san francisco":
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "welcome to the san francisco health plan your call may be monitored or recorded for quality assurance purposes"):
                return {"response": "", "to_say": False}
            elif voice_input == "spell espanol":
                return {"response": "", "to_say": False}
            elif voice_input == "but i expand yol":
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "if at any time you wish to be connected to our customer service department press zero to skip this greeting", errors_allowed=8):
                return {"response": "0", "to_say": False}
            elif check_regex(voice_input, "press zero to skip the screen or assistant menu please press star or pound"):
                return {"response": "0", "to_say": False}
            elif check_regex(voice_input, "member eligibility using the members 11 digit sfhp ID number please press one to enter the members nine-digit social security number please press two to enter the", errors_allowed=13):
                return {"response": "0", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18008777703':
            # Manhatten life insurance
            if check_regex(voice_input, "if you are provider calling for benefits eligibility or claim status please visit our website at provider manhattan or press seven"):
                return {"response": "7", "to_say": False}
            elif check_regex(voice_input, "please listen carefully as our menu options have changed"):
                return {"response": "", "to_say": False}
        
        elif full_prompt_row['phone_number'] == '+18008002254':
            # Bankers life and casualty
            if check_regex(voice_input, "press one if you are a doctor hospital or provider press two if you are not a policy holder"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "calling colonial penn life insurance company at affiliate of bankers life if you are a policy holder"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "listen closely as our options for service have changed"):
                return {"response": "policy information", "to_say": True}
            elif voice_input == "okay policy information":
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "the providers nine digit social security or tax id number"):
                to_use = input_data_dict["provider_tax_id"].replace(
                    " ", "").replace(".", "").replace("-", "")
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "which was that a social security number or tax id number"):
                return {"response": "tax I.D. number", "to_say": True}
            elif check_regex(voice_input, "youd like to speak with a customer service representative correct"):
                return {"response": "Yes", "to_say": True}
            elif check_regex(voice_input, "say repeat that"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "if that was a social security number press one if it was a tax id number press two"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "whats the policy number"):
                return {"response": input_data_dict["member_id"], "to_say": False}
            elif check_regex(voice_input, "you can say planes information benefits status"):
                return {"response": "benefits", "to_say": False}

        # Specific testing
        elif full_prompt_row['phone_number'] == '+19165555555':
            if 'press one' in voice_input.lower() or 'press 1' in voice_input.lower():
                return {"response": "1", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18882729272':
            # Second transamerica number
            if check_regex(
                voice_input,
                "select from the following menu options at any time for claims or benefit eligibility press one for all other services",
                    errors_allowed=8):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, " if youre a physician or healthcare professional serving a patient please press one for all other calls please press two"):
                return {"response": "1", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18552789329':
            # Combined insurance for member ids that start with 0
            if voice_input == "thank you for":
                return {"response": "", "to_say": False}
            elif voice_input == "thank you for calling combined insurance":
                return {"response": "", "to_say": False}
            elif voice_input == "thank you for calling":
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "if you are an agent please press one"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "to verify policy benefits please press one for the status of a claim please press two", errors_allowed=8):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for an agent please press one for all other callers"):
                return {"response": "2", "to_say": False}
        elif full_prompt_row['phone_number'] == '+18004455747':
            # Hills insurance
            if check_regex(
                voice_input,
                "if youre calling from a physicians office press one if you are a member or want to learn more about a member press two for all other callers press three and thank you for calling hill physicians medical group your call will be recorded for quality and training purposes",
                    errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if youre calling from a physicians office press one if you are a member or want to learn more about a member press two for all other callers press three", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if youre calling from a physicians office press one if you are a member or want to learn more about becoming a member press two for all other calls press three", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "thank you for calling hill physicians medical group your call will be recorded for quality and training purposes"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "hmo press one for ppo press two"):
                return {"response": "", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18443804556':
            # WEB TPA
            if check_regex(
                    voice_input,
                    "if you are a provider calling in regards to the status of a claim press one for all other inquiries please press two"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "please hang up and dial 911 the hartford is enabled medicare crossover for all of our members cause its medicare crossover"):
                return {"response": "", "to_say": False}
            elif voice_input == "thank you for calling":
                return {"response": "", "to_say": False}
            elif voice_input == "thank you for calling the hartford":
                return {"response": "", "to_say": False}
            elif voice_input == "thank you for calling the hartford customer care center this is a medical emergency please hang up and dial 911":
                return {"response": "", "to_say": False}
        elif full_prompt_row['phone_number'] == '+18005327575':
            # Health Plans Inc Harvard Pilgram
            if check_regex(
                voice_input,
                "please press one members please press two all other calls",
                    errors_allowed=4):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "press two all other callers, please. Press zero to speak to an operator", errors_allowed=4):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if this is a medical emergency please hang up and dial 911 conversations are recorded for quality assurance purposes", errors_allowed=4):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "providers please press one members please press two all other calls please press zero", errors_allowed=6):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "press two all other callers please press zero to speak to an operator thank you", errors_allowed=4):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if your call is to confirm a patients eligibility please press 1 to check the status of a claim", errors_allowed=4):
                return {"response": "1", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18553837248':
            heuristic_result = anthem_responses(voice_input, input_data_dict)
            if "response" in heuristic_result:
                return heuristic_result
        elif full_prompt_row['phone_number'] == '+18667730404':
            # Tricare for Life Medicare Supplement
            if check_regex(
                voice_input,
                "thank you for calling wps military and veterans health care claims administrator for access to all of your needs visit us on our website at tricare4ucom tricare the number for the letter u",
                    errors_allowed=10):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "thank you for calling wps military and veterans health care claims administrator for access to all of your needs visit us on our website at", errors_allowed=6):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "thank you for calling wps military and veterans house claims administrator for access to all of your needs visit us on our website at"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "military and veterans health care claims administrator for access to all your needs visit us on our website at tricare", errors_allowed=6):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "are you a doctor or hospital or claim processor please say yes or no"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "you can say eligibility and benefits claim status or more options"):
                return {"response": "eligibility and benefits", "to_say": True}
            elif check_regex(voice_input, "would you like to hear information about a patients eligibility"):
                return {"response": "eligibility", "to_say": True}
            elif check_regex(voice_input, "i need your nine digit tax id"):
                return {
                    "response": input_data_dict["provider_tax_id"],
                    "to_say": True}
            elif check_regex(voice_input, "i didnt hear you are you a doctor or hospital"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "hospital or claim processor please say yes or no"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "whats the beneficiaries"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "repeat that general benefits main menu or goodbye or if you would like to check"):
                return {"response": "representative", "to_say": True}
            elif check_regex(voice_input, "if you would like to check another patient please tell me the patient sponsor number"):
                return {"response": "respresentative", "to_say": True}
            elif check_regex(voice_input, "you can also say main menu or goodbye"):
                return {"response": "respresentative", "to_say": True}

        elif full_prompt_row['phone_number'] == '+17185607605':
            # ROJW Health Care Support (Medicare Supplement)
            if check_regex(
                voice_input,
                "press two for a reservation of services such as radiology tests surgical procedures or inpatient services press three for claim status",
                    errors_allowed=6):
                return {"response": "4", "to_say": False}
            elif check_regex(voice_input, "press one for our business address fax number or email press two for authorization of services such as radiology tests surgical procedures or inpatient services", errors_allowed=6):
                return {"response": "4", "to_say": False}
        elif full_prompt_row['phone_number'] == '+18666853330':
            # UMR
            if check_regex(
                    voice_input,
                    "thank you for calling the provider line at Quantum health for eligibility verification of medical benefits"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "would you like to speak with a care coordinator for further assistance"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "care coordinator for further assistance"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "care coordinators are currently assisting other callers for convenience visit our newly"):
                return {"response": "", "to_say": True}

        elif full_prompt_row['phone_number'] == '+16267080333':
            # Imperial Health Holdings
            if check_regex(voice_input, "to continue in english press one"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "health plan of california press one for imperial insurance company press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "press one for our eligibility department press two for claims please press three for provider services or contract press four for prospective members", errors_allowed=8):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "eligibility department press two for claims please press three for provider services or contracting press four for prospective members", errors_allowed=8):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "thank you for calling imperial health plan if california if this is a member with a lifethreatening emergency please hang up and dial", errors_allowed=8):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "thank you for calling imperial health plan of california if this is a member with a lifethreatening emergency please hang up and dial"):
                return {"response": "", "to_say": False}
            # comment

        elif full_prompt_row['phone_number'] == '+18007777898':
            # western growers
            if check_regex(
                voice_input,
                "for claim status press one for eligibility and benefits press two to return to the main menu press pound for me to hear these options again",
                    errors_allowed=6):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "for claim status press one for eligibility and benefits press two to return to the main menu press pound to hear these options again"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "please enter your nine digit tax id"):
                to_use = input_data_dict["provider_tax_id"].replace(
                    " ", "").replace(".", "").replace("-", "")
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "for hcid starting with w press one for h c i d starting with any other letter press to use the subscribers social security"):
                if input_data_dict["member_id"][0] == "W":
                    return {"response": "1", "to_say": False}
                else:
                    return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "for hcid starting with w press one for starting with any other letter press two to use the subscribers"):
                if input_data_dict["member_id"][0] == "W":
                    return {"response": "1", "to_say": False}
                else:
                    return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "for hcid starting with w press one for each cid starting with any other letter press two"):
                if input_data_dict["member_id"][0] == "W":
                    return {"response": "1", "to_say": False}
                else:
                    return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "please enter the eight digits that follow the w on the h c i d"):
                to_use = input_data_dict["member_id"].replace(
                    " ", "").replace(".", "").replace("-", "")
                to_use = to_use[1:]
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "please enter the patients 8digit date of birth enter two digits for the month two digits for the day and four digits for the year"):
                member_date_of_birth = input_data_dict["member_date_of_birth"]
                dob_list = member_date_of_birth.split(" ")
                month = mappings.MONTH_STR_TO_NUM[dob_list[0].lower()]
                day = dob_list[1].replace(", ", "").replace(",", "")
                str_to_use = month + day + dob_list[2]
                return {"response": str_to_use, "to_say": False}
            elif check_regex(voice_input, "for claim status for this or another participant press three to return to the main menu press four or to speak to a customer service representative press zero", errors_allowed=10):
                return {"response": "0", "to_say": False}
            elif check_regex(voice_input, "for claim status press one for eligibility and benefits press two to return to the main menu press pound cake these options again", 8):
                return {"response": "2", "to_say": False}

            respond_one_phrases = [
                ("benefits information for this participant press one to hear eligibility or benefits information for a different participant press two for claim status for this or another participant press three to return to the main menu", 4),
                ("for medical eligibility and benefit information press one press two vision press three pharmacy press four", 7),
                ("for information press one temple press two vision press three for our menu press four to hear this menu again press the star key to return to the previous menu press pound", 4),
                ("for eligibility and benefit information press two to repeat this menu press the star key to return", 4),
                ("for medical eligibility and benefit information press one simple press two vision press three for me to hear this menu again", 4),
                ("for medical eligibility and benefit information press one simple press two vision press three for me press four to hear this menu again", 8),
                ("if this is correct press one to enter press two to return to the previous menu", 4),
                ("if this is correct press one page to reenter press two to return to the previous menu press pound", 4),
                ("if this is correct press one for me to reenter press two to return to the previous menu", 4),
                ("should number for this call press one", 4),
                ("prior authorization press three for mailing address or information on electronic claims set up press four if you are a provider calling in regards to joining our network box or a", 8),
                ("press two for pharmacy prior authorization press three for mailing address or information on electronic claims set up press four if you are a provider calling", 6),
                ("press one for information press two for pharmacy prior authorization press three for mailing address or information on electronic claims settlement press four", 4),
                ("claim status or eligibility and benefit information press one for information press two for pharmacy prior authorization press three", 4),
                ("to hear the confirmation number for this call press one", 4),
                ("if you are a provider press one if you are a subscriber calling about your own individual or family insurance plan press two", 4),
                ("families insurance plan press two if you are an employer press three", 4),
                ("if you are a provider press one if you are a subscriber calling about your own individual or familys insurance plan press two if you are", 4),
                ("to number for this call press one", 2),
                ("eligibility and benefit information press one central press two vision press three pharmacy press four to hear this menu again press the star key for me to return", 8),
                ("benefit information press one dental press two vision press three pharmacy press four to hear this menu again press the star key to return to the previous menu", 8),
                ("more information on electronic claims set up press four if you are a provider calling in regards to joining our network the status of a loa or a w9 issue press five", 6),
                ("if this is correct press one to reenter page press two to return to the previous menu press pound", 4),
                ("is correct press one to reenter press two to return to the previous menu press pound", 4),
                ("press one to reenter press two to return to the previous menu press pound", 4),
                ("if this is correct press one to juice press two to return to the previous menu press pound", 4),
                ("if this is correct press one to better answer press two to return to the previous menu, press pound", 4),
                ("for medical eligibility and benefit information press one dental press two vision press three pharmacy choice for me to hear this menu", 8),
                ("press two vision press three pharmacy press four to hear this menu again press the star key to return to the previous menu press pound for me", 8),
                ("if this is correct press one to speak press two to return to the previous menu, press pound", 4)
            ]

            for phrase in respond_one_phrases:
                if check_regex(
                        voice_input,
                        phrase[0],
                        errors_allowed=phrase[1]):
                    return {"response": "1", "to_say": False}

            no_response_exact_match = [
                "thank you for",
                "for this call press one",
                "thank you",
                "thank you for this call may be monitored",
                "more online visit us at www",
                "and more online visit us at www"
                "thank you for calling",
                "for purposes but espanyol",
                "thank you for customer service",
                "call press one",
            ]
            for phrase in no_response_exact_match:
                if voice_input == phrase:
                    return {"response": "", "to_say": True}

            no_response_fuzzy_match = [
                ("your confirmation number for this call is", 4),
                ("repeat the confirmation number press star", 4),
                ("and click on the office link to hear this message again press one", 4),
                ("thank you for customer service team this call may be monitored and recorded for quality and training purposes", 4),
                ("and click on the opus link to hear this message again press one", 4),
                ("and click on the link to hear this message again press one", 4),
                ("may be monitored and recorded for quality assurance and training purposes but espanyol", 4),
                ("this call may be monitored and recorded for quality assurance and training purposes", 4),
                ("did you know you can access patients benefit and eligibility information check claim status and more online visit us", 4),
                ("the assurance trust customer service team this call may be monitored and recorded for quality assurance and training purposes", 6),
                ("may be monitored and recorded for quality assurance and training purposes but espanyol police unit off", 4),
                ("the customer service team this call may be monitored and recorded for quality assurance and training purposes", 4),
                ("confirmation number for this call is", 1),
                ("and recorded for quality assurance and training purposes but espanyol pretty soon it off", 4),
                ("formation number for this call is", 4),
                ("please enjoy our selfserve system as our customer service office is currently closed customer service is open monday to friday from 7 am to 5:30 pacific standard time but espanyol pretty soon at those", 10),
                ("thank you for calling the customer service team this call may be monitored and recorded for quality and training purposes", 6),
                ("thank you for calling the western growers assurance trust customer service team this call may be monitored and recorded for quality assurance and training purposes", 6),
                ("this call may be monitored and recorded for quality assurance and training purposes", 4),
                ("thank you for calling the customer service team this call may be monitored and", 2)
            ]

            for phrase in no_response_fuzzy_match:
                if check_regex(
                        voice_input,
                        phrase[0],
                        errors_allowed=phrase[1]):
                    return {"response": "", "to_say": True}
        elif full_prompt_row['phone_number'] == '+18008540186':
            # Transamerica
            if check_regex(
                voice_input,
                "thank you for calling transamerica insurance companies please listen carefully as our menu options have changed if youre interested in product information or wish to purchase a new policy please press one if youre calling for assistance on an existing policy please press two for all other policies including life accident and cancer coverage please press three",
                    errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif voice_input == "thats www":
                return {"response": "", "to_say": False}
            elif voice_input == "www":
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "you can now access medicare supplement information on our website"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "if youre a physician or healthcare professionals serving a patient please press one if you are a customer calling to file a claim please press two for calling to check on a status of a claim or have questions about a claim payment please press three", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "healthcare professionals serving a patient please press one if you are a customer calling to file a claim please press two if youre calling to check on a status of a claim or have any questions about a claim payment please press three", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "please press two if youre calling to check on a status of a claim or have questions about a claim payment please press three for all other questions please press four", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for medicare supplement or retiree medical insurance please press one if you're calling about retiree medical coverage please press two"):
                return {"response": "", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18007003874':
            # Central California Alliance for Health
            if check_regex(
                voice_input,
                "in the central california alliance for health to continue in english press one for the continued are in espanol or prima dos",
                    errors_allowed=6):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "california alliance for health to continue in english press one for the continual in espanyol or prima"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for calling the central california alliance for health to continue in english press one", errors_allowed=6):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for the central california alliance for health to continue in english press one"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for help to continue in english press one spell continued are in espanol"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for calling the central california alliance for health to continue in english press one spell continued are in espanyol or prima", errors_allowed=6):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "central california alliance for health to continue in english press one but i continued are in espanyol or prima"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if this is a medical emergency hang up and dial 911 or go to the nearest emergency room if you know your partys extension dial it now if you're an alliance member press one if you are a doctor or provider press two for office hours locations and our website address press three to return to the previous menu press nine", errors_allowed=10):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "please listen carefully as our menu options have changed for eligibility and benefits information press one for claims inquiries press two for pharmacy press three for authorization inquiries, press four Care Management, press five for health education and cultural and linguistic Services, press six for transportation", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "please listen carefully as our menu options have changed for eligibility and benefits information press one for claims inquiries press two for the office press three for authorization inquiries press four for care management press five for health education and cultural and linguistic services press six for transportation", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "thank you for calling central california alliance for health automated system to listen to the message about subcontracted services press pound now"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "thank you for calling central california alliance for health automated eligibility system to listen to the message about subcontracted services press pound now", errors_allowed=6):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "options have changed for eligibility and benefits information press one for claims inquiries press two for pharmacy wage at 3 for authorization inquiries press four for care management press five for health education and cultural and linguistic services press six for transportation press seven for all other doctor or provider inquiries", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "if the id number is not available you may use the members social security number not all plans require members to register by social security number to enter a letter press the star key and follow the instructions", errors_allowed=8):
                string_to_use = map_alphanumeric_to_keypad_star(
                    input_data_dict["member_id"])
                print(string_to_use)
                return {"response": string_to_use, "to_say": False}
            elif check_regex(voice_input, "digit plan id number followed by the pound key if the id number is not available you may use the members social security number not all plans require members to register by social security number to better press the star key", errors_allowed=8):
                string_to_use = map_alphanumeric_to_keypad_star(
                    input_data_dict["member_id"])
                print(string_to_use)
                return {"response": string_to_use, "to_say": False}
            elif check_regex(voice_input, "if this is correct press one otherwise press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "for the current day month and year press one otherwise to enter a specific date press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "to hear the confirmation number again press one otherwise press two"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "to check eligibility for another date of service press one if youd like to check eligibility for another member press two to exit press nine"):
                return {"response": "9", "to_say": False}
            elif check_regex(voice_input, "if you know your partys extension dial it out if youre an alliance member press one if you are a doctor or providers press two for office hours locations and our website address press three to return to the previous menu press nine"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "changed for eligibility and benefits information, press one for claims inquiries, press two for pharmacy, press down for authorization inquiries, press four for Care Management, press five for health education and cultural and", errors_allowed=10):
                return {"response": "2", "to_say": False}

        elif full_prompt_row['phone_number'] == '+18884218444':
            # Valley Health Plan (HMO)
            heuristic_result = valley_health_plan_eligibility_heuristics_18884218444(
                voice_input, input_data_dict)
            if "response" in heuristic_result:
                return heuristic_result
            # elif check_regex(voice_input, "thank you")
        elif full_prompt_row['phone_number'] == '+18007084414':
            # United Healthcare, Harvard Pilgrim
            member_id_response = [
                ("if you are calling for a member whos identification number begins with hp press one for a member whos identification number is all numeric press two", 8),
                ("calling for a member whose identification number begins with h p press one for a member whose identification number is all numeric press two", 8),
                ("whos identification number begins with h p press one for a member whose identification number is all numeric press two", 4),
                ("if you are calling about a member whose identification number begins with h p press one to use our self service options for a member", 4),
                ("identification number begins with h p press one for a member whose identification number is all numeric press two", 4),
                ("if you are calling about a member whose identification number begins with h p press one to use our self service options home or a member whos identification number is all numeric press two", 10)
            ]

            for phrase in member_id_response:
                if check_regex(
                        voice_input,
                        phrase[0],
                        errors_allowed=phrase[1]):
                    if input_data_dict["member_id"][0:4] == "H. P":
                        return {"response": "1", "to_say": False}
                    else:
                        return {"response": "2", "to_say": False}

            press_seven_respond = [
                ("if you have a question about electronic transmissions press three for adi to reach the insurance liability and recovery department press four for behavioral health services press five if you have questions about our website h ph connect for providers press six for all other inquiries including but not limited to benefits claim status eligibility and referrals press seven", 14),
                ("for ati to reach the insurance liability and recovery department press four for behavioral health services press five if you have questions about our website for providers press six for all other inquiries including but not limited to benefits claim status eligibility and referrals press seven", 14),
                ("to reach the insurance liability and recovery department press four for behavioral health services press five if you have questions about our website for providers press six for all other inquiries including but not limited to benefits claim status eligibility and referrals press seven", 14),
                ("to reach the insurance liability and recovery department press four for behavioral health services press five if you have questions about our website h ph connect for providers press six for all other inquiries including but not limited to benefits claim status eligibility page press seven", 14),
                ("press one for advanced imaging services through nih press two if you have a question about electronic data transmissions press three for adi to reach the insurance liability and recovery department press four", 10),
                ("press one for advanced imaging services through prestone know if you have a question about electronic data transmissions press three for edi to reach the insurance liability and recovery department press four", 10)

            ]

            for phrase in press_seven_respond:
                if check_regex(
                        voice_input,
                        phrase[0],
                        errors_allowed=phrase[1]):
                    return {"response": "7", "to_say": False}

            if check_regex(
                    voice_input,
                    "we are here to help you thank you for calling the center at harvard pilgrim health care we are here to help you"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "to get started whats your npi"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "which of the following, can i help you with You can say verify coverage claim status referral authorizations appeals for calling about something else"):
                return {"response": "verify coverage", "to_say": True}
            elif check_regex(voice_input, "please tell me the members harvard pilgrim id number including the letters at the beginning or say or enter the members nine digit social security number"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "id number including the letters at the beginning or say or enter the members ninedigit social security number"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "sorry i didnt hear that please say or enter the 10 digit"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "you can either say your ten digit national provider id or you can enter it on the telephone key pad otherwise say I don't have one"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif voice_input == "to get started":
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif voice_input == "thanks and the members date of birth":
                return {
                    "response": input_data_dict["member_date_of_birth"],
                    "to_say": True}
            elif check_regex(voice_input, "wait times may be significant we apologize for the inconvenience did you know that you can find the information you need quickly using our secure"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "high volume of provider calls and wait times may be significant name is for the inconvenience did you know that you can find the information you need quickly using our secure h ph connect portal for a variety of self service functions for more information please refer to our faq on to help", errors_allowed=12):
                return {"response": "", "to_say": False}

            no_response_exact = [
                "thank you for",
                "thank you for calling",
                "thank you for calling the",
                "all right",
                "flash provider",
                "we are here to help you for quality purposes calls may be monitored and recorded"
            ]
            for phrase in no_response_exact:
                if voice_input == phrase:
                    return {"response": "", "to_say": False}

        elif full_prompt_row['phone_number'] == '+14088854080':
            # Valley Health Plan (HMO) Again
            # WORK IN PROGRESS, I DON"T KNOW WHAT TO PRESS
            if check_regex(
                voice_input,
                "press two for administration press three for utilization management press four for provider relations press five for health education press six for marketing press seven to repeat this menu",
                    errors_allowed=8):
                return {"response": "5", "to_say": False}
            elif check_regex(voice_input, "press two for administration press three for utilization management prep for for provider relations press five for health education press six for marketing press seven to repeat this menu", errors_allowed=8):
                return {"response": "5", "to_say": False}
            elif check_regex(voice_input, "hello you have reached valley health plan if this is a lifethreatening emergency please hang up and dial 911"):
                return {"response": "", "to_say": True}
        elif full_prompt_row['phone_number'] == '+18555701600':
            # Aspire Medicare Advantage
            if check_regex(
                    voice_input,
                    "if you are a member please press one if you are a provider please press two if you are a broker please press three for more information about a spire health plan please press four for all other questions please press five"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "if you are a provider please press two if you are a broker please press three for more information about a spire health plan please press four for all other questions"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "thank you for calling provider services if you have questions about part d prescription drug benefits press one for help regarding a medicare advantage member press two for help regarding commercial plans press three to return to the main menu press nine"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "thank you for calling aspire health plan if this is a medical emergency please hang up and dial 911"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "aspire health plan if you are calling because this is a medical emergency please hang up and dial 911"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "thank you for calling aspire health plan if you are calling because this is a medical emergency please hang up and dial 911"):
                return {"response": "", "to_say": True}
            elif voice_input == "may i dont know":
                return {"response": "", "to_say": True}
        elif full_prompt_row['phone_number'] == '+18316570700':
            # Coastal Healthcare Aministrators
            pass
        elif full_prompt_row['phone_number'] == '+18006776669':
            # BLUE CROSS OF CALIFORNIA (PPO)
            if check_regex(
                    voice_input,
                    "welcome to the anthem blue cross provider service department if this is a medical emergency please hang up and dial 911 your call may be monitored or recorded for quality assurance"):
                return {"response": "", "to_say": True}
            elif check_regex("are generally sent to the member except when federal or state mandates apply or negotiated agreements are in place", voice_input):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "tell me or enter your 10 digit npi or your nine digit tax id", errors_allowed=6):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif voice_input == "i have the member records":
                return {"response": "", "to_say": True}
            elif voice_input == "your records":
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "provider are generally sent to the member except when federal or state mandates apply or negotiated agreements are in place now tell me or enter your provider id", errors_allowed=6):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "tell me or enter your 10digit npi or your nine digit tax id"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "say your ten digit npi or your ninedigit tax id or enter it on your telephone keypad"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "are you calling for eligibility status or something"):
                return {
                    "response": "Eligibility status",
                    "to_say": True}
            elif voice_input == "payments for services rendered by a nonparticipating provider are generally sent to the member except when federal or state mandates apply or negotiated agreements are in place":
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "now you can say repeat that fax it switch member switch provider or main menu"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "just say eligibility and benefits or press one claims or press two press certification or press three or say more options press four"):
                return {"response": "Eligibility and benefits", "to_say": True}
            elif check_regex(voice_input, "you can i get a repeat that fax it switch member switch provider or main menu"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "you can say repeat that fax it switch member switch off or main menu"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "tell me or enter your provider id", errors_allowed=2):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "pacific time friday you can access our website www"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "disability in benefits claims precertification or more options"):
                return {"response": "Eligibility and benefits", "to_say": True}
            elif voice_input == "the member records":
                return {"response": "Eligibility and benefits", "to_say": True}
            elif voice_input == "more options":
                return {"response": "Eligibility and benefits", "to_say": True}
            elif voice_input == "or enter your provider id":
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif voice_input == "for me or enter your provider id":
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "i didnt hear you just say your ten digit npi or your nine digit tax id or enter it on your telephone keypad"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif voice_input == "your provider id":
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "now tell me the member id including any letters"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}

        elif full_prompt_row['phone_number'] == '+18006762583' or full_prompt_row['phone_number'] == '+18005416652':
            # Blue Shield of California (PPO)

            if check_regex(
                    voice_input,
                    "am i speaking with a healthcare provider"):
                return {"response": "Yes, I am a provider", "to_say": True}
            elif check_regex(voice_input, "please say or gender the 10digit national provider number or nine digit tax id"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "providers to determine a patients benefit eligibility and precertification information am i speaking with the healthcare provider"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "please say or enter the 10digit national provider number or nine digit tax id", errors_allowed=8):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "please say or enter the 10 digit number or a tax id if you are a member calling with questions say member", errors_allowed=2):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "calls may be monitored or recorded please say or enter the 10digit national provider number or a tax id", errors_allowed=8):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "are you calling for precertification benefits and eligibility or both"):
                return {"response": "benefits and eligibility", "to_say": True}
            elif check_regex(voice_input, "but if its an eligibility or both"):
                return {"response": "Benefits and Eligibility", "to_say": True}
            elif "certain eligibility or both" == voice_input:
                return {"response": "Benefits and Eligibility", "to_say": True}
            elif "may say claims" == voice_input:
                return {"response": "eligibility", "to_say": True}
            elif "or say its something else" == voice_input:
                return {"response": "eligibility", "to_say": True}
            elif "benefits and eligibility or both" == voice_input:
                return {"response": "Benefits and Eligibility", "to_say": True}
            elif "espanyol" == voice_input:
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "need to look up the plan if you need time to get the member information say hold on otherwise say or enter the subscriber id number or the social security number of the person"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "now we need to look up the plan if you need time to get the member information say hold on otherwise say or enter the subscriber id number or the social security number of the person"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif "its an eligibility or both" == voice_input:
                return {"response": "benefits and eligibility", "to_say": True}
            elif check_regex(voice_input, "what are the first three characters of the patients member id you can tell me the letters or use the phonetic alphabet such as"):
                first_three = input_data_dict["member_id"][0:7]
                to_say = [mappings.PHONETIC_ALPHABET_DICT[x]
                          for x in first_three if x in mappings.PHONETIC_ALPHABET_DICT]
                to_say = " ".join(to_say)
                return {"response": to_say, "to_say": True}
            elif check_regex(voice_input, "you can tell me the letters or use the phonetic alphabet such as foxtrot zulu juliet 4 ft jaye what are the first three characters", errors_allowed=10):
                first_three = input_data_dict["member_id"][0:7]
                to_say = [mappings.PHONETIC_ALPHABET_DICT[x]
                          for x in first_three if x in mappings.PHONETIC_ALPHABET_DICT]
                to_say = " ".join(to_say)
                return {"response": to_say, "to_say": True}
            elif check_regex(voice_input, "you can tell me the characters for example e l b or you can use the phonetic alphabet like echo bravo so what are the the first three", errors_allowed=8):
                first_three = input_data_dict["member_id"][0:7]
                to_say = [mappings.PHONETIC_ALPHABET_DICT[x]
                          for x in first_three if x in mappings.PHONETIC_ALPHABET_DICT]
                to_say = " ".join(to_say)
                return {"response": to_say, "to_say": True}
            elif check_regex(voice_input, "what are the first three characters of the patients you can tell me the letters or use the phonetic alphabet such as"):
                first_three = input_data_dict["member_id"][0:7]
                to_say = [mappings.PHONETIC_ALPHABET_DICT[x]
                          for x in first_three if x in mappings.PHONETIC_ALPHABET_DICT]
                to_say = " ".join(to_say)
                return {"response": to_say, "to_say": True}
            elif check_regex(voice_input, "did you say representative"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "to do something else say main menu or if youre finished feel free to hang up"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "hi thank you for calling blue shield of california this is nick how may i help you today", errors_allowed=8):
                dr_name = input_data_dict["provider_name"]
                intro_response = f"My name is Riley Jones and I'm calling on behalf of Dr. {dr_name}'s office on a recorded line. I'm looking for information on a member's eligibility and benefits."
                return {"response": intro_response, "to_say": True}
            elif check_regex(voice_input, "are you calling as a provider from a billing office or mso office"):
                dr_name = input_data_dict["provider_name"]
                intro_response = f"My name is Riley Jones and I'm calling on behalf of Dr. {dr_name}'s office on a recorded line. I'm looking for information on a member's eligibility and benefits."
                return {"response": intro_response, "to_say": True}
            elif check_regex(voice_input, "s as in sierra"):
                return {"response": "Yes", "to_say": True}
            elif check_regex(voice_input, "one moment while i look that up"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "claim status press one for benefits and deductibles press two for medical authorizations press three or four member eligibility"):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "may say claims benefits"):
                return {"response": "benefits", "to_say": True}
            elif check_regex(voice_input, "press one for benefits and deductibles press two for medical authorizations press three or four member please press four for anything else press five"):
                return {"response": "2", "to_say": False}

            no_response_fuzzy_match = [
                ("if this is a medical emergency please hang up and call nineoneone calls may be monitored or recorded", 4),
                ("thank you for calling blue card eligibility if this is a medical emergency please hang up and call 911 and thank you for calling blue card eligibility", 4),
                ("this line is for health care providers to determine", 4),
                ("please hang up and call 911", 4)
            ]

            for phrase in no_response_fuzzy_match:
                if check_regex(
                        voice_input,
                        phrase[0],
                        errors_allowed=phrase[1]):
                    return {"response": "", "to_say": True}

            no_response_exact_match = [
                "hang up and call nineoneone calls may be monitored or recorded by the by",
                "mercatos",
                "friday spaniol",
                "friday spaniol mercatos",
                "about a spaniol mercatos",
                "but marcatos",
                "but by noon mercatos",
                "okay which do you need",
                "this line is for health care providers to determine a",
                "this line is 4",
                "thank you for calling",
                "thank you",
                "but a spaniol mercatos",
                "main menu say claims",
                "the appropriate blue cross blue shield plans",
                "but a fine young mercatos",
                "but marche",
                "but by noon marcatos",
                "thank you for calling blue card eligibility"
                "but i get",
                "thank you for"]

            for phrase in no_response_exact_match:
                if voice_input == phrase:
                    return {"response": "", "to_say": True}

        elif full_prompt_row['phone_number'] == '+18008248839':
            # BLUE SHIELD OF CALIFORNIA - FEP (PPO)
            if check_regex(
                    voice_input,
                    "now i need the subscriber id this can be found on the member id card please say the id including the letters and followed by the numbers"):
                return input_data_dict["member_id"], True
            elif check_regex(voice_input, "are you calling today as a healthcare professional say yes no or im not sure"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "is a healthcare professional say yes no or im not sure"):
                return {"response": "yes", "to_say": True}
            elif check_regex(voice_input, "ability or say its something else"):
                return {"response": "eligibility", "to_say": True}
            elif voice_input == "thank you for calling blue shield federal employee program":
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "press one benefits or press two authorizations or three eligibility or four or say its something else"):
                return {"response": "eligibility", "to_say": True}
            elif check_regex(voice_input, "for another member say another member to do something else say main menu or if youre finished feel free to hang up"):
                return {"response": "representative", "to_say": True}
            elif check_regex(voice_input, "say its something else", errors_allowed=2):
                return {"response": "eligibility", "to_say": True}
        elif full_prompt_row['phone_number'] == '+18778423210' or '+18005428789':
            # UNITED HEALTHCARE (PPO)
            if "united healthcare" == voice_input:
                return {"response": "", "to_say": True}
            elif "scare" == voice_input:
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "for assistance with your or a family members health plan say im a member otherwise in a few words tell me why youre calling today"):
                return {"response": "Eligibility", "to_say": True}
            elif check_regex(voice_input, "for what member id", errors_allowed=2):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "say or enter the member id of the patient you are calling about"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "sorry i didnt understand here are some examples of things you can say claim status or authorization for surgery so tell me what can I help you with today", errors_allowed=10):
                return {"response": "eligibility and benefits", "to_say": True}
            elif check_regex(voice_input, "say or enter the 10 digit npi"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "are you calling about medicare medicaid or something else"):
                return {"response": "Something else", "to_say": True}
            elif check_regex(voice_input, "okay do you want the member information to be faxed"):
                return {"response": "No", "to_say": True}
            elif check_regex(voice_input, "do you want a reference number for this number"):
                return {"response": "Yes", "to_say": True}
            elif check_regex(voice_input, "you can say check another member advocate or main menu"):
                return {"response": "Advocate", "to_say": True}
            elif check_regex(voice_input, "thanks just a moment while i get your account details whats the npi"):
                return {
                    "response": input_data_dict["provider_npi"],
                    "to_say": True}
            elif check_regex(voice_input, "do you need information for eligibility pcp deductibles copay or coinsurance you can also say give me a summary"):
                return {"response": "Give me a summary", "to_say": True}
            elif check_regex(voice_input, "if youd like to hear them benefits summary again just say repeat"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "please stay on them for assistance with your or a family members health plan say im a member otherwise in a few words tell me why youre calling today"):
                return {"response": "Eligibility", "to_say": True}
            elif check_regex(voice_input, "now you can say repeat or to hear outofnetwork info saved more"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "now you can say repeat or to hear outofnetwork info more"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "may be monitored or recorded for quality if youre calling about cove and 19 claims for the uninsured or provider relief fund press seven", errors_allowed=10):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "may be monitored or recorded for quality if youre calling about covent nineteen claims for the uninsured or provider relief fund press seven", errors_allowed=10):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "you with the right advocate i will need a little more information which of the following can I help you with benefits and eligibility claims authorization", errors_allowed=10):
                return {"response": "benefits and eligibility", "to_say": True}
            elif check_regex(voice_input, "thanks just a moment while i get your account details"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "whats the tax id number"):
                return {
                    "response": input_data_dict["provider_tax_id"],
                    "to_say": True}

        elif full_prompt_row['phone_number'] == '+18886323862' or full_prompt_row['phone_number'] == '+18006240756':
            # AETNA (EPO)
            if check_regex(
                voice_input,
                "thank you for calling to improve our service your call will be monitored and recorded please say or enter your npi or tax id",
                    errors_allowed=6):
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif "enter the patience" == voice_input:
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif "one moment please" == voice_input:
                return {"response": "", "to_say": True}
            elif "please say or enter the patience" == voice_input:
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "thank you for calling aetnas dedicated provider service center to improve our service your call will be monitored and recorded please say or enter your npi or tax id", errors_allowed=6):
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "i need to identify the provider youre calling for say or enter your npi or tax id if youre not a medical or dental professional say im a member for more information"):
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "monitored and recorded please say or enter your npi or tax id"):
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "your call will be monitored and recorded please say or enter your npi or tax id"):
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif check_regex("thank you for calling", voice_input, errors_allowed=0):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "if its or press two precertification or press three or contact information or press four"):
                return {"response": "Coverage and Benefits", "to_say": True}
            elif check_regex(voice_input, "say claims or press one coverage and benefits or press two precertification or press three or contact information or press four"):
                return {"response": "Coverage and Benefits", "to_say": True}
            elif check_regex(voice_input, "please say or enter the patients so that i can service and route your call effectively if you dont provide the id you may experience longer wait time zone necessary transfers if the id begins with a w or is all numbers just enter the numbers otherwise say the id"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "to receive the information via fax say have it faxed or press two"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "you can also say main menu or press six for more information say help or press star or if youre done say goodbye or just hang up"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "now you can say repeat that or press one fax it or press two or for this patients a check another service or press three you can also say next patient or press four or claims address or press five for anything else say main menu or press six or if youre done say goodbye or just hang up", errors_allowed=10):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "if you have another patient youd like to get eligibility and benefits for say next patient or press four or for our claims mailing address and pay r i d say claims address or press five", errors_allowed=8):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "to find out if theyre covered for another service type say check another service or press three to get coverage information for a different person"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "youre done with this call correct"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "they check another service or press three to get coverage information for a different person say next patient or press four or to hear the address to send your claims"):
                return {"response": "Representative", "to_say": True}
            elif check_regex(voice_input, "routine eye exam six maternity 7 or well baby care 8 to choose from a list of the most common service types i can help you with say list them or press 12 or to tell me another service type say check another service or press 13", errors_allowed=10):
                return {"response": "Specialist Office Visit", "to_say": True}
            elif check_regex(voice_input, "you want to speak with a representative correct"):
                return {"response": "Yes", "to_say": True}
            elif check_regex(voice_input, "prince number for all the information youll hear on this call is a va 15433 7 to 6 to 5 to 2"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "please say or enter the patients so that i can service and route your call effectively if you dont provide the id you may experience longer wait times or unnecessary transfers if the id begins with a w or is all numbers just enter the numbers"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "say or enter the patients so that i can service and route your call effectively if you dont provide the id you may experience longer wait time"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "tell me the service type like office visit sick or physical therapy for the most common service types say list them or press one"):
                return {"response": "Specialist Office Visit", "to_say": True}
            elif check_regex(voice_input, "for a list of the most common types say list them or press one you can also say the service type name like a outpatient hospital or say or enter the ansi service type code like 40 or 50 for more information say help or press star", errors_allowed=8):
                return {"response": "Specialist Office Visit", "to_say": True}
            elif voice_input == "who is waived":
                return {"response": "", "to_say": True}
            elif voice_input == "in our records do you want to try the date of birth again say yes or press one no two":
                return {"response": "Yes", "to_say": True}
            elif check_regex(voice_input, "what would you like next say try another patient or press one main menu or press two or representative"):
                return {"response": "Representative", "to_say": True}
            elif voice_input == "specialist office visit is covered on this plan":
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "may i have your name", errors_allowed=2):
                dr_name = input_data_dict["provider_name"]
                intro_response = f"My name is Riley Jones and I'm calling on behalf of Dr. {dr_name}'s office on a recorded line. I'm looking for information on a member's eligibility and benefits."
                return {"response": intro_response, "to_say": True}
            elif voice_input == "coverage for the patience":
                return {"response": "", "to_say": True}
            elif voice_input == "your enter the patience":
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "coverage your enter the patience"):
                return {
                    "response": input_data_dict["member_id"],
                    "to_say": True}
            elif check_regex(voice_input, "now enter a say the patients date of birth"):
                return {
                    "response": input_data_dict["member_date_of_birth"],
                    "to_say": True}
        elif full_prompt_row['phone_number'] == '+18004074627':
            # BC medi-caid
            if check_regex(
                    voice_input,
                    "your pharmacy benefits are no longer handled by anthem but by medical rx if you need to reach your pharmacy benefit manager please call me back at 8009772273 you can also visit their website at medical"):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "for calling anthem blue cross to continue this call in english cest english or press one but i couldnt be modestly your mother n espanol porfavor", errors_allowed=6):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "emergency please hang up and dial 911 or go to the nearest emergency room and just so you know calls may be monitored or recorded for quality purposes are you a plan member or a provider"):
                return {"response": "Provider", "to_say": True}
            elif check_regex(voice_input, "what would you like you can say fax back eligibility coverage claims medical treatment authorization or mental health or substance abuse authorization code", errors_allowed=6):
                return {"response": "Eligibility", "to_say": True}
            elif check_regex(voice_input, "your pharmacy benefits are no longer handled by anthem but by medical rx if you need to reach your pharmacy benefit manager please call me at 8972273 you can also visit their website at medical rx", errors_allowed=10):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "your pharmacy benefits are no longer handled by anthem but by medical rx if you need to reach your pharmacy benefit manager please call medical rx8 8009772273 you can also visit their website at", errors_allowed=10):
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "so you know calls may be monitored or recorded for quality purposes are you a plan member or a provider"):
                return {"response": "Provider", "to_say": True}
            elif check_regex(voice_input, "im sorry im having difficulty validating your information if you are calling about longterm services say longterm services otherwise say medical"):
                return {"response": "Medical", "to_say": True}
            elif check_regex(voice_input, "thank you for calling anthem blue cross to continue this call in english cest english or press one"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "enter your 10 digit national provider identification number or your nine digit tax identification number", errors_allowed=6):
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif voice_input == "your provider identification number":
                to_use = input_data_dict["provider_npi"].replace(
                    " ", "").replace(".", "")
                return {"response": to_use, "to_say": False}
            elif check_regex(voice_input, "calling anthem blue cross to continue this call in english say english or press one but i couldnt be more freedom in espanol"):
                return {"response": "1", "to_say": False}
        elif full_prompt_row['phone_number'] == '+18886248258':
            # Cigna - GWH
            if check_regex(
                    voice_input,
                    "for english please press one for spanish please press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "thank you for calling benefit and risk management services if you are a provider please press one if you are a member please press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "thank you for calling benefit and risk management"):
                # Keep this one at the bottom because the longer strings with
                # this should have priority
                return {"response": "", "to_say": True}
            elif check_regex(voice_input, "for claims press two for additional service options press three"):
                return {"response": "1", "to_say": True}
        elif full_prompt_row['phone_number'] == '+18002286080':
            # Medico insurance
            if check_regex(
                voice_input,
                "press one followed by the four digit extension number if you are a policyholder press two if you are an agent press three months if you are a medical provider press four if you are interested in our health products",
                    errors_allowed=8):
                return {"response": "4", "to_say": False}
            elif check_regex(voice_input, "if you are calling for benefit information press one for claim status press two for all other questions press three", errors_allowed=6):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "press one for claim status press two if you have questions on a virtual credit card payment press three thousand address information press four for all other questions", errors_allowed=10):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "please enter the 12 digit alphanumeric policy number please include any preceding zeros"):
                member_id_to_use = map_alphanumeric_to_keypad(
                    input_data_dict["member_id"])
                return {"response": member_id_to_use, "to_say": False}
            elif check_regex(voice_input, "please enter the insurance date of birth using two digits for the month two digits for the day and four digits for the year"):
                member_date_of_birth = input_data_dict["member_date_of_birth"]
                dob_list = member_date_of_birth.split(" ")
                month = mappings.MONTH_STR_TO_NUM[dob_list[0].lower()]
                day = dob_list[1].replace(", ", "").replace(",", "")
                str_to_use = month + day + dob_list[2]
                return {"response": str_to_use, "to_say": False}
            elif check_regex(voice_input, "if this is correct press one if not press two"):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "to speak to a representative press eight to hear these options again press 9"):
                return {"response": "8", "to_say": False}
            elif check_regex(voice_input, "thank you for calling medical insurance company a well a b company your call may be recorded to ensure quality service"):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "thank you for calling medical insurance company a well a b company if you are a policyholder press one if you are an agent press two if you are a medical provider", errors_allowed=10):
                return {"response": "3", "to_say": False}
            elif voice_input == "press two if you are a medical provider press three":
                return {"response": "3", "to_say": False}
            elif check_regex(voice_input, "for policy holder press one if you are an agent press two if you are a medical provider press three"):
                return {"response": "3", "to_say": False}
            elif check_regex(voice_input, "well abby company if you are a policyholder press one if you are an agent press two if you are a medical provider press three"):
                return {"response": "3", "to_say": False}
            elif check_regex(voice_input, "thank you for calling medical insurance company a well a b company if you are a policyholder press one if you are an agent press two if you are a medical provider press"):
                return {"response": "3", "to_say": False}
            elif check_regex(voice_input, "calling about benefit information ress one for claim status press two if you have questions on a virtual credit card payment press three for a drug information press four", errors_allowed=8):
                return {"response": "1", "to_say": False}
            elif check_regex(voice_input, "may either speak the insurance date of birth and a format of march sixteenth nineteen ninety or enter it into digit month to digiday four digit year on your touch-tone keypad month", errors_allowed=10):
                member_date_of_birth = input_data_dict["member_date_of_birth"]
                dob_list = member_date_of_birth.split(" ")
                month = mappings.MONTH_STR_TO_NUM[dob_list[0].lower()]
                day = dob_list[1].replace(", ", "").replace(",", "")
                str_to_use = month + day + dob_list[2]
                return {"response": str_to_use, "to_say": False}

        elif full_prompt_row['phone_number'] == '+18004585736':
            # AMA
            if voice_input == "you have reached the insurance agency":
                return {"response": "2", "to_say": False}
            elif voice_input == "you have reached the ama insurance agency":
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "press one for claim related questions or to verify benefits press two to obtain a quote or purchase insurance press three to check the status of an application for insurance press four", errors_allowed=10):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "if you are an insured calling to report or inquire about a claim press one if you are a provider press two for our mailing address press three", errors_allowed=6):
                return {"response": "2", "to_say": False}
            elif check_regex(voice_input, "verification of eligibility and benefits its not a guarantee of payment benefits are held to all policy provisions including preexisting conditions coordination of benefits and other plan limitations", errors_allowed=10):
                return {"response": "", "to_say": False}
            elif check_regex(voice_input, "verification of eligibility and our benefits is not a guarantee of payment benefits are held to all policy provisions including preexisting conditions coordination of benefits and other plan limitations", errors_allowed=10):
                return {"response": "", "to_say": False}

        elif full_prompt_row['phone_numer'] == '+16189613103':
            if "press one" or "press 1" in voice_input:
                return {"response": "1", "to_say": False}

    return {}


def general_heuristics(voice_input, input_data_dict):
    provider_name = input_data_dict["provider_group_name"]
    intro_response = f"Hi! My name is Riley Jones and I'm calling on behalf of {provider_name} on a recorded line. I'm looking for some eligibility and benefits information for a specialist office visit for a patient."

    intro_phrases = [
        ("may i have your first and last name", 2),
        ("may i start by getting your first and last name", 2),
        ("my name is anna your provider service advocate may i have your name please", 6),
        ("you are speaking with nancy provide a service advocate may i have your name", 6),
        ("my name is bertha and how can i assist you", 6),
        ("thank you for calling firehouse this is jasmine how may i help you", 6),
        ("check thank you for calling firehouse on april speaking how may i help you", 6),
        ("thank you for calling is firehouse on april speaking how may i help you", 6),
        ("thank you for calling us firehouse on april speaking how may i help you", 6),
        ("thank you for calling customer support my name is theresa may i have your name please", 7),
        ("thanks for choosing customer care renee speaking how can i assist you", 6),
        ("probably help phone number services how can i help you", 4),
        ("member services how can i help you", 4),
        ("provider services advocates can i have your name and initial of your last name please", 4),
        ("my name is cambria how can i help you today", 6),
        ("who do i have the pleasure of speaking with", 4),
        ("my name is theresa may i have your name please", 6),
    ]

    for phrase in intro_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": intro_response, "to_say": True}

    no_response_phrases = [
        ("your call will be answered by the next available representative", 4),
    ]

    for phrase in no_response_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": "", "to_say": True}
    return {}


def map_alphanumeric_to_keypad(string_to_use):
    cleaned_string = string_to_use.replace('.', '').replace(' ', '')
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    letters = list(string.ascii_uppercase)
    new_string = ''
    for character in cleaned_string:
        if character in numbers:
            new_string += character
        elif character in letters:
            new_string += mappings.KEYPAD_MAPPING[character]
        else:
            print("ERROR: Character not found")
    return new_string


def valley_health_plan_eligibility_heuristics_18884218444(
        voice_input, input_data_dict):

    respond_one_phrases = [
        ("please press one for assistance and english", 4),
        ("listen carefully to all options before making your selection if you are able to help plan member insured through an employer group", 4),
        ("if you are a valley health plan member please press one", 4),
        ("if you are a member insured through an employer group covered california or individual and family plan please press one", 4),
        ("please listen carefully to all options before making your selection if you spell re valley health plan member insured through an employer group covered california or individual and family plan please press one if", 8),
        ("please listen carefully to all options before making your selection if you are in a valley health plan member insured through an employer group covered california or individual and family plan please press one if you are a physician a doctors office or facility", 8),
        ("listen carefully to all options before making your selection if you are a health plan member insured through an employer group covered california or individual and family plan please press one", 8),
        ("listen carefully to all options before making a selection if you are a valley health plan member insured through an employer group covered california or individual and family plan", 8),
        ("for member services eligibility and benefit questions or shoppers please press one for providers with a claim inquiry or claim status question", 4),
        ("eligibility and benefit questions or shoppers please press one for providers with a claim inquiry or claim status question please press two", 4),
        ("for member services eligibility and benefit questions or shoppers please press one for providers with a claim inquiry or claim status please press two", 6)
    ]

    for phrase in respond_one_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": "1", "to_say": False}

    respond_differently = [
        ("if you are a covered california or individual and family plan member press three if you are a member of an employer group press four",
         4),
        ("if you are a covered california home or individual and family plan member press three if you are a member of an employer group press four", 4)
    ]

    for phrase in respond_differently:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            member_id = input_data_dict["member_id"]
            if member_id[0] == "9":
                return {"response": "4", "to_say": False}
            else:
                return {"response": "3", "to_say": False}

    respond_two_phrases = [
        # ("if you are a physician a doctors office or facility please press two", 4),
        # ("eligibility authorization status and benefits please press two for covered california member services benefits coverage and authorization status please press three for pendant or previously submitted authorizations", 10),
        # ("eligibility authorization status and benefits please press two for covered california member services benefits package and authorization status please press three for pendant or previously submitted authorizations", 10),
        # ("two for covered california member services benefits coverage and authorization status please press three for ended or previously submitted authorizations please press four for provider contracts please press five for disputes and grievances please", 10),
        # ("two for covered california member services off if its coverage and authorization status please press three for ended or previously submitted authorizations please press four for provider contracts please press five", 10),
        # ("two for covered california member services benefits coverage and authorization status please press three for it or previously submitted authorizations please press four for provider contracts please press five for disputes and grievances", 10),
        ("for pharmacy questions please contact our pharmacy benefit manager by pressing one for all other members service questions please press two", 4)
    ]

    for phrase in respond_two_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": "2", "to_say": False}

    dont_respond_phrases = [
        ("thank you for calling valley health plan you have reached the provider services telephone directory please listen to this message and its entirety before making your selection as our menu options have changed the provider relations department is open monday through friday 8 am to 5 pm you may also send your questions by email to provider relations", 4),
        ("cc g o v", 2),
        ("we appreciate your patience your call will be answered by the next available representative", 4),
        ("our representatives are currently assisting other callers your call is important to us please continue to hold and your call will be answered by the next available representative", 4)
    ]

    for phrase in dont_respond_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": "", "to_say": True}

    return {}


def alignment_health_care_eligibility_heuristics(
        voice_input, input_data_dict):

    respond_two_phrases = [
        ("member press one if you are a provider press two if you are interested in becoming a member or would like information regarding alignment health services press three", 6),
        ("member press one if you are a provider press two if you are interested in becoming a member or would like information regarding alignment health services", 6),
        ("member press one if you are a provider press two if you are interested in becoming a member or would like information regarding alignment health services office press three", 6),
        ("eligibility benefits verification press two for prior authorization status press three for hospital admissions press four for network management questions regarding a product or provider portal assistance press five", 6),
        ("verification press two for prior authorization status press three for hospital admissions press four for network management questions regarding a product or provider portal assistance press five", 6),
        ("eligibility benefits verification press two for prior authorization status press three for hospital admissions press four for network management questions regarding a product or provider portal assistance", 6),
        ("eligibility benefits verification press two for prior authorization status press three month for hospital admissions press four for network management questions regarding a product or provider portal assistance press five", 6),
        ("eligibility benefits verification press two for prior authorization status prep for hospital admissions press four for network management questions regarding a product or provider portal assistance press five", 6),
        ("if you would like to enter your responses with a keypad press one or if you would like to speak your responses press two", 6),
        ("would like to enter your responses with a keypad press one or if you would like to speak your responses press two", 4),
        ("if you are a provider press two if you are interested in becoming a member or would like information regarding alignment health services press three if you know the party you would like to speak to press for", 6),
        ("if you are a provider press two if you are interested in becoming a member or would like information regarding alignment to help services press three", 6)
    ]

    for phrase in respond_two_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": "2", "to_say": False}

    if check_regex(
            voice_input,
            "plan benefits and eligibility information for a specific member plan press two followed by the pound"):
        return {"response": "2#", "to_say": False}
    elif check_regex(voice_input, "additional benefits information check another members plan look up a general plan speak to a representative or im finished"):
        return {"response": "Speak to a representative", "to_say": True}
    elif check_regex(voice_input, "whats your tax identification number or tin please enter it now followed by pound button"):
        return {"response": input_data_dict["provider_tax_id"], "to_say": True}
    elif check_regex(voice_input, "please state your national provider identifier or npi whats your npi number"):
        return {"response": input_data_dict["provider_npi"], "to_say": True}
    elif check_regex(voice_input, "you will need to speak your responses for general plan benefits and eligibility confirmation say general information if you nee-d plan benefits and eligibility information for a specific member plan say member specific plan"):
        return {"response": "member specific plan", "to_say": True}
    elif check_regex(voice_input, "please press 1 if yes followed by the pound button or press two if thats the incorrect npi followed by the pound button"):
        return {"response": "1#", "to_say": False}
    elif check_regex(voice_input, "please press 1 if yes followed by the pound button or press two thousand that is the incorrect npi followed by the pound button"):
        return {"response": "1#", "to_say": False}
    elif check_regex(voice_input, "please press 1 if yes followed by the pound button or press two if that is the incorrect npi number followed by the pound button"):
        return {"response": "1#", "to_say": False}
    elif check_regex(voice_input, "press one followed by the pound button for alignment member id or press two followed by the pound button for m bi if you do not have the member id or m bi number press three followed by the pound button", errors_allowed=8):
        return {"response": "1#", "to_say": False}
    elif check_regex(voice_input, "you can find the member id on the left side of the alignment member id card please input the member id followed by the pound button"):
        string_to_use = input_data_dict["member_id"] + "#"
        string_to_use = string_to_use.replace(" ", "").replace(".", "")
        return {"response": string_to_use, "to_say": False}
    elif check_regex(voice_input, "you can find the member id on the left side of the alignment member id card please say the member id one number at a time", 6):
        return {"response": input_data_dict["member_id"], "to_say": True}
    elif check_regex(voice_input, "if that was correct press one followed by the pound button otherwise press two followed by the pound button"):
        return {"response": "1#", "to_say": False}
    elif check_regex(voice_input, "whats your tax identification number or tin"):
        return {"response": input_data_dict["provider_tax_id"], "to_say": True}
    elif check_regex(voice_input, "the patients account with the alignment member id or the medicare beneficiary identifier or m bi which of these would you like to use say alignment member id or m bi"):
        return {"response": "Alignment Member ID", "to_say": True}
    elif check_regex(voice_input, "send a fax containing the benefit details", 2):
        return {"response": "No", "to_say": True}
    elif check_regex(voice_input, "back on to continue with the benefits details", 2):
        return {"response": "No", "to_say": True}
    elif check_regex(voice_input, "it may take a few seconds to look up that plan is that okay", 4):
        return {"response": "Yes", "to_say": True}
    elif check_regex(voice_input, "copay for each medicare covered service do you want to continue with the benefits details", 4):
        return {"response": "No", "to_say": True}

    no_response_fuzzy_phrases = [
        ("thank you for calling alignment help", 4),
        ("have you downloaded the new alignment", 4),
        ("if this is a life threatening medical emergency please hang up and dial 911", 4),
        ("please hang up and dial 911", 4),
        ("provider portal at alignment health plan", 4),
        ("jen thats www", 2),
        ("have you downloaded the new alignment health plan mobile apps", 4),
        ("thank you for calling the alignment health plan provider line providers may verify eligibility through our online portal", 4),
    ]

    for phrase in no_response_fuzzy_phrases:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {"response": "", "to_say": True}

    no_response_exact_match = [
        "thank you for calling help",
        "female",
        "welcome to a line",
        "welcome to alignment",
        "welcome to alignment help",
        "thank you for calling",
        "scheduling your appointment today",
        "our dedicated",
        "welcome to a",
        "welcome to help",
        "thank you for calling to help",
        "911 for quality purposes this call may be recorded",
        "will u w w alignment",
        "wwwcom"
    ]

    for phrase in no_response_exact_match:
        if voice_input == phrase:
            return {"response": "", "to_say": True}

    no_response_remove_from_transcript_fuzzy = [
        ("covered services send secure messages to your concierge team find a doctor or urgent care and more search for alignment health plan in the apple store or google play download it today", 4),
        ("offered the best care possible please let us know if theres anything we can do differently to better serve our members alignment healthcare is always here for you", 4),
        ("always easy to get the care treatment or test you need please let our dedicated specialists help you in scheduling your appointment today alignment healthcare is always here to help", 4),
        ("an automatic callback which enables you to retain your position in the queue we will call you back once you have reached the front of the queue if you wish to request a callback press nine", 4),
        ("health plan mobile apps we improve this mobile app with you in mind giving you secure access to your health care information anywhere and at anytime check your benefits and covered services send secure messages to your concierge team find a doctor or urgent care and more search for alignment health plan in the apple store or google play and download it today", 4),
        ("customer service representatives are trained to listen to you carefully and treat you with courtesy and respect we are always here to help you", 8),
        ("our friendly customer service representatives are always happy to help you complete the forms and show you how easy they are to fill out", 6),
        ("we have dedicated doctors who spend time listening to you carefully and explain everything our doctors are here to help you", 4),
        ("alignment healthcare is always here to help you along your health journey", 4),
        ("we understand that your time is valuable it can be frustrating to wait to see your doctor", 4),
        ("we make it easy for you to get the medicines your doctor ordered", 4),
        ("giving you secure access to your health care information", 2),
        ("doctor or urgent care and more search for alignment health plan in the apple store or google play and download it today", 4),
        ("have you downloaded the new alignment", 0),
        ("check your benefits and covered services send secure messages to your concierge team find a doctor or urgent care and more search for alignment health plan in the apple store or play and download it today", 6),
        ("your possible please let us know if theres anything we can do differently to better serve our members alignment healthcare is always here for you", 4),
        ("dedicated Specialists help you in scheduling your appointment", 4)

    ]

    for phrase in no_response_remove_from_transcript_fuzzy:
        if check_regex(voice_input, phrase[0], errors_allowed=phrase[1]):
            return {
                "response": "",
                "to_say": True,
                "remove_from_transcript": True}
    return {}


def anthem_responses(voice_input_punc, input_data):
    # This is from the test anthem data
    voice_input_tmp = voice_input_punc.lower().translate(
        str.maketrans('', '', string.punctuation))
    voice_input = re.sub(r'\s+', ' ', voice_input_tmp)

    if check_regex(
            voice_input,
            "to continue this call in english press one") or check_regex(
            voice_input,
            "this call in english press one"):
        return {"response": "1", "to_say": False}
    elif check_regex(voice_input, "can i get your first and last name", errors_allowed=1):
        input_data_dict = json.loads(input_data)
        member_name = input_data_dict["member_name"]
        response_to_use = f"My name is Riley Jones and I'm calling on behalf of member {member_name} on a recorded line, and I've been authorized to verify her benefits",
        return {"response": response_to_use, "to_say": True}
    elif check_regex(voice_input, "may I have your first and last name", errors_allowed=1):
        input_data_dict = json.loads(input_data)
        member_name = input_data_dict["member_name"]
        response_to_use = f"My name is Riley Jones and I'm calling on behalf of member {member_name} on a recorded line, and I've been authorized to verify her benefits",
        return {"response": response_to_use, "to_say": True}
    elif check_regex(voice_input, "may i start by getting your first and last name", errors_allowed=1):
        input_data_dict = json.loads(input_data)
        member_name = input_data_dict["member_name"]
        response_to_use = f"My name is Riley Jones and I'm calling on behalf of member {member_name} on a recorded line, and I've been authorized to verify her benefits",
        return {"response": response_to_use, "to_say": True}
    elif voice_input.endswith("your call may be monitored or recorded for quality assurance"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("your call may be monitored"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("make a quick one time premium payment online at anthem"):
        return {"response": "", "to_say": True}
    # elif check_regex(voice_input, "What is the member zip code"):
    #    return "9. 5. 6. 6. 1.", True
    elif check_regex(voice_input, "press one to start texting instead of remaining on the phone"):
        return {"response": "", "to_say": True}
    elif check_regex(voice_input, "are you currently a member"):
        return {"response": "yes", "to_say": True}
    elif check_regex(voice_input, "would you like to hear information about our mobile app sydney"):
        return {"response": "no", "to_say": True}
    elif check_regex(voice_input, "in a few words please tell me what you are calling about"):
        return {"response": "benefits information", "to_say": True}
    elif check_regex(voice_input, "you want benefits is that right"):
        return {"response": "yes", "to_say": True}
    # elif check_regex(voice_input, "What is the date of birth"):
    #    return "October 1, 1985", True
    elif check_regex(voice_input, "what type of benefit are you calling about"):
        return {"response": "Medical", "to_say": True}
    # Below are related to the Kaiser call
    # elif check_regex(voice_input, "enter the members medical health record number") or \
    #        check_regex(voice_input, "Medical health record number one digit at a time") or \
    #        check_regex(voice_input, "Please say or enter the member's medical record number"):
    #    return "7 5 0 0 4 9 0", False
    elif voice_input.endswith("thank you for calling the kaiser permanente"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("eligibility and claim status inquiries must be obtained online using our self-service tool please visit"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("we may record or monitor your call") or \
            voice_input.endswith("we may record or monitor your call") or \
            voice_input.endswith("member service contact center") or \
            voice_input.endswith("do you"):
        return {"response": "", "to_say": True}
    elif check_regex(voice_input, "eligibility benefits or claims"):
        return {"response": "benefits", "to_say": True}
    elif check_regex(voice_input, "i heard benefits is that right"):
        return {"response": "yes", "to_say": True}
    # elif check_regex(voice_input, "I heard seven five zero zero four nine zero, is that right?") or \
    #        check_regex(voice_input, "I heard 7 5 0 0 4 9 0 is that right?"):
    #    return "yes", True
    # elif check_regex(voice_input, "patient hospital lab and x-ray optical or outpatient behavioral health"):
    #    return "primary care physician visits", True
    # elif check_regex(voice_input, "And what date do you want?"):
    #    return "March 14, 2023", True
    elif check_regex(voice_input, "would you like to hear your confirmation number"):
        return {"response": "yes", "to_say": True}
    elif voice_input.endswith("this benefit started on march 14"):
        return {"response": "", "to_say": True}
    # For United Healthcare
    elif voice_input.endswith("are you a healthcare provider or a member") or \
            voice_input.endswith("are you a healthcare provider or a member"):
        return {"response": "member", "to_say": True}
    # elif check_regex(voice_input, "what is your date of birth?"):
    #    return "September 18, 1993", True
    elif check_regex(voice_input, "medical policy mental health and substance abuse prescriptions dental vision or say something else"):
        return {"response": "a medical policy", "to_say": True}
    elif voice_input.endswith("united healthcare"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("this call may be monitored or recorded for quality"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("but espanol or prima todays") or \
            voice_input.endswith("but i espanol or prima todays"):
        return {"response": "", "to_say": True}
    elif voice_input.endswith("so you can more easily be identified on your next call"):
        return {"response": "No", "to_say": True}
    elif voice_input.endswith("in a few words tell me why you're calling today") or \
            voice_input.endswith("tell me why you're calling today"):
        return {
            "response": "I'm calling about medical benefits information",
            "to_say": True}
    elif check_regex(voice_input, "spell your first and last name", 2):
        return {
            "response": "R. I. L. E. Y. space J. O. N. E. S.",
            "to_say": True}
    elif voice_input.endswith("thank you for calling the kaiser permanente center"):
        return {"response": "", "to_say": True}
    return {}

from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField
from local_groups.models import Group
    
#TODO: automate endorsement -> approval -> candidates page 
    
class Nomination(models.Model):
    """
    A nomination is filled out by the group with basic information about the group's nomination process and reasons why a candidate or initiative should be endorsed.
    """    
    
    #TODO: remove group info from here because it's attached to application which this is attached to
    group_name = models.CharField(max_length=64, null=True, blank=False, verbose_name="Group Name")
    group_id = models.CharField(max_length=4,null=True, blank=False, verbose_name="Group ID")  
    
    rep_email = models.EmailField(null=True, blank=False, verbose_name="Contact Email", max_length=254)
    rep_first_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="First Name")
    rep_last_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="Last Name")
    rep_phone = PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    
    #TODO: replicate whatever we do in Application
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_state = USStateField(max_length=2, null=True, blank=False)

    group_nomination_process = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Group Nomination Process") 
    
    candidate_progressive_champion = models.TextField(max_length=500, blank=False, null=True, verbose_name = "How is the candidate a progressive champion?")
    candidate_community = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What has the candidate done for the community?")
    candidate_presidential_support = models.BooleanField(default=False, blank=False, verbose_name = "Did the candidate publicly support anyone in the Primaries or/and General Elections for President in 2016?")
    candidate_presidential_support_who = models.TextField(max_length=128, blank=True, null=True, verbose_name = "If yes, who?")
    candidate_platform = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Briefly describe the candidate's platform?")
    candidate_goals = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What are some of the candidate's top goals?")
    candidate_plan = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What does the candidate plan to accomplish while in office?")
    candidate_group_organizing = models.BooleanField(default=False, blank=False, verbose_name = "Are people in the nominating Our Revolution group willing to organize for the candidate?")
    candidate_group_organizing_actions = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What actions will the group take and how many people have agreed to volunteer/work?")
    candidiate_importance_of_endorsement = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Why is an our Revolution national endorsement important in this race?")
    
    def __unicode__(self):
        return str(self.group_name + ' - ' + self.candidate_first_name + ' ' + self.candidate_last_name)

class Questionnaire(models.Model):
    """
    A platform questionnaire is filled out by the candidate with basic information and in-depth policy positions.
    """    
    
    #TODO: replicate whatever we do in Application
    #TODO: make sure we're getting all office/district/location info we need
     
    # Candidate Information and Social Media
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_email = models.EmailField(null=True, blank=False, verbose_name="Candidate Email", max_length=255)
    candidate_phone = PhoneNumberField(null=True, blank=True, verbose_name="Candidate Phone Number")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_state = USStateField(max_length=2, null=True, blank=False)
    candidate_website_url = models.URLField(null=True, blank=True, verbose_name="Candidate Website URL", max_length=255)
    candidate_facebook_url = models.URLField(null=True, blank=True, verbose_name="Candidate Facebook URL", max_length=255)
    candidate_twitter_url = models.URLField(null=True, blank=True, verbose_name="Candidate Twitter URL", max_length=255)
    candidate_instagram_url = models.URLField(null=True, blank=True, verbose_name="Candidate Instagram URL", max_length=255)
    candidate_youtube_url = models.URLField(null=True, blank=True, verbose_name="Candidate YouTube URL", max_length=255)
    
    # TODO: donation links 
    
    # TODO: Make questions their own model
    # Multiple Choices
    QUESTIONNAIRE_CHOICES = (
        ('a', 'Agree'),
        ('b', 'Disagree'),
        ('c', 'Mostly agree'),
        ('d', 'Mostly disagree'),
    )
    
    # Income and Wealth Inequality
    question_wealthy_fair_share = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Today, we live in the richest country in the history of the world, but that reality means little because much of that wealth is controlled by a tiny handful of individuals. To address that, the wealthy and large corporations must pay their fair share in taxes.")
    position_wealthy_fair_share = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_too_big_to_fail = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Huge financial institutions must be broken up so they are no longer too big to fail.")
    position_too_big_to_fail = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_minimum_wage = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="No one who works 40-hours a week should live in poverty. The minimum wage needs to be a livable wage of $15 an hour.")
    position_minimum_wage = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_youth_jobs = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="It is critically important to create jobs for disadvantaged young Americans by investing in a youth jobs programs.")
    platform_youth_jobs = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_social_security = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Social Security must be expanded so that every American can retire with dignity.")
    platform_social_security = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    # Trade
    question_trade_deals = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Trade deals like TPP, NAFTA, CAFTA, and PNTR have cost the U.S. thousands of jobs, allowed corporations to shut down operations in the US and move work to low-wage countries where people are forced to work for pennies an hour. We must do everything we can to reverse these effects from current trade deals and ensure we don't sign on to anymore that place corporate profits ahead of working class and poor people in the U.S. and throughout the world.")
    platform_trade_deals = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    # Campaign Finance Reform
    question_citizens_united = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Citizens United, a 5-4 Supreme Court decision, resulted in enabling the wealthiest people and largest corporations in this country to contribute unlimited amounts of money to campaigns. This decision must be overturned and corruption in politics must end. This means fighting to pass a constitutional amendment making it clear that Congress and the states have the power to regulate money in elections. We must also eliminate super PACs and other outside spending abuses and work to aggressively enforce campaign finance rules.")
    platform_citizens_united = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_right_to_vote = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="In order to protect our democracy, we must fight for a publicly financed, transparent system of campaign financing that amplifies small donations. We must also ensure that all Americans are guaranteed an effective right to vote.")
    platform_right_to_vote = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Education
    question_college = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Every American who studies hard in school should be able to go to college regardless of how much money their parents make and without going deeply into debt. For that, we need to work towards making tuition free at public colleges and universities throughout America, stopping the federal government from making a profit on student loans.")
    platform_college = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Healthcare
    question_healthcare = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Healthcare is a human right. Our healthcare system needs to work for all of us. We must guarantee healthcare as a right of citizenship by enacting a Medicare for all single-payer healthcare system, as well as lowering the price for prescription drugs.")
    platform_healthcare = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Infrastructure
    question_infrastructure = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The U.S.'s infrastructure, from our roads and bridges, to our dams, waterways and electrical grid, have not been properly invested in nor used the advances in technology for maintenance or improvements. America is long overdue to rebuild our crumbling roads, bridges, railways, airports, public transit systems, ports, dams, wastewater plants, and other infrastructure needs.")
    platform_infrastructure = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_defense_spending = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The U.S. defense spending is larger than that of the next seven largest defense budgets. We must firmly reject any increase to defense spending at the cost of cuts to domestic social spending.")
    platform_defense_spending = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Environment
    question_climate_change = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The United States must lead the world in tackling climate change, if we are to make certain that this planet is habitable for our children and grandchildren. We must transform our energy system away from polluting fossil fuels, and towards energy efficiency and sustainability.")
    platform_climate_change = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Racial Justice
    question_racial_justice = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="African-Americans and Latinos are twice as likely to be arrested and almost four times as likely to experience the use of force during encounters with the police. They also comprise well over half of all prisoners, even though African-Americans and Latinos make up approximately one quarter of the total US population. We must change this by de-militarizing our police forces, ban for-profit prisons, turn back from the War on Drugs, eliminate mandatory minimums, and increase investment in programs that help individuals recover from substance abuse and mental health problems.")
    platform_racial_justice = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Immigration
    question_undocumented_immigration = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Despite the central role immigrants play in our economy and in our daily lives, undocumented workers are reviled by some for political gain and shunted into the shadows. It is time for this disgraceful situation to end. We must pave the way for a swift legislative path to citizenship for 11 million undocumented immigrants and protect programs like DACA.")
    platform_undocumented_immigration = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_deportation_machine = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The inhumane deportation machine must be dismantled by ending deportation programs, closing down private detention centers, offering humane treatment and asylum to victims of violence and minors fleeing from dangerous circumstances.")
    platform_deportation_machine = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Foreign Policy
    question_peace = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The U.S. must move away from a policy of unilateral military action, and toward a policy of emphasizing compassion, diplomacy, and ensuring the decision to go to war is a last resort.")
    platform_peace = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    question_palestine_israel = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The U.S. must have a just approach to the Palestinian and Israeli conflict; one that supports Israels right to exist and that denounces human rights abuses and crimes against humanity committed by the state of Israel against the Palestinian people.")
    platform_palestine_israel = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Women's Rights
    question_pay_equity = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Do everything possible to ensure pay equity for women.")
    platform_pay_equity = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    question_reproductive_rights = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Expand and protect the reproductive rights of women")
    platform_reproductive_rights = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #LGBT Rights
    question_lgbt = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The United States has made remarkable progress on gay rights in a relatively short amount of time. But there is still much work to be done. In many states, it is still legal to fire someone for being gay. It is legal to deny someone housing for being transgender. That is unacceptable and must change. We must end discrimination in all forms.")
    platform_lgbt = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Native American Rights
    question_native_rights = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="The United States must not just honor Native American treaty rights and tribal sovereignty, it must also move away from a relationship of paternalism and control, and toward one of deference and support. That means supporting tribal sovereignty and tribal jurisdiction, honoring the treaties and federal statutes, improving housing and education, as well as by protecting sacred places and Native American cultures.")
    platform_native_rights = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Veterans
    question_veterans = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="As a nation, we have a moral obligation to provide the best quality care to those who have put their lives on the line to defend us. Taking care of our veterans is a cost of war. The Department of Veterans Affairs must be fully funding and expanded so that every veteran gets the care that they have earned and deserve. Additionally, claim processing, mental health and dental services, and access to the VA must be improved.")
    platform_veterans = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Candidate's position on this issue:")
    
    #Local Issues
    question_local_issues = models.CharField(max_length=1,blank=False, null=True, choices=QUESTIONNAIRE_CHOICES, verbose_name="Briefly list important local issues included in your platform.")
    
    def __unicode__(self):
        return str(self.candidate_first_name + ' ' + self.candidate_last_name)

class Application(models.Model):
    """
    An application is a single submission for an endorsement. Each application consists of a group nomination and a candidate questionnaire, and has a many-to-one relationship with a group.
    """
    
    create_dt = models.DateTimeField(auto_now_add=True)
    
    nomination = models.OneToOneField(
        Nomination,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True
    )
    
    #TODO: change to foreign key
    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True
    )
    
    #TODO: change to foreign key
    group_name = models.CharField(max_length=64, null=True, blank=False, verbose_name="Group Name")
    group_id = models.CharField(max_length=4,null=True, blank=False, verbose_name="Group ID")  
    
    rep_email = models.EmailField(null=True, blank=False, verbose_name="Contact Email", max_length=254)
    rep_first_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="First Name")
    rep_last_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="Last Name")
    rep_phone = PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    
    #TODO: change to foreign key and create new object for each new candidate, implement autocomplete to  minimize duplicate candidates
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_state = USStateField(max_length=2, null=True, blank=False)
    
    #TODO: Flesh out (get with E and G to figure out statuses)
    STATUSES = (
       ('incomplete', 'Incomplete'),
       ('submitted', 'Submitted'),
       ('approved', 'Approved'),
       ('removed', 'Denied')
   ) 
    status = models.CharField(max_length=16, choices=STATUSES, default='incomplete')
    
    def __unicode__(self):
        return str(self.group_name + ' - ' + self.candidate_first_name + ' ' + self.candidate_last_name)
    

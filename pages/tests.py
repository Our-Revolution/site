from django.test import Client
from django.test.runner import DiscoverRunner
from unittest import TestCase 



class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation """

    def setup_databases(self, **kwargs):
        """ Override the database creation defined in parent class """
        pass

    def teardown_databases(self, old_config, **kwargs):
        """ Override the database teardown defined in parent class """
        pass


class RoutesTestCase(TestCase):
    allow_database_queries = True

    
    def setUp(self):
        self.client = Client()


    def test_about(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
    

    def test_act(self):
        response = self.client.get('/act/')
        self.assertEqual(response.status_code, 301)
    

    def test_action(self):
        response = self.client.get('/action/')
        self.assertEqual(response.status_code, 200)
    

    def test_august_30_primary_candidates(self):
        response = self.client.get('/august-30-primary-candidates/')
        self.assertEqual(response.status_code, 301)
    

    def test_bylaws_redirect(self):
        response = self.client.get('/page/bylaws/')
        self.assertEqual(response.status_code, 301)

    def test_bylaws(self):
        response = self.client.get('/bylaws/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidate_questionnaire(self):
        response = self.client.get('/candidate-questionnaire/')
        self.assertEqual(response.status_code, 301)
    

    def test_candidates(self):
        response = self.client.get('/candidates/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_adam_dahl(self):
        response = self.client.get('/candidates/adam-dahl/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_adrian_fontes(self):
        response = self.client.get('/candidates/adrian-fontes/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_anabel_larumbe(self):
        response = self.client.get('/candidates/anabel-larumbe/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_andru_volinsky(self):
        response = self.client.get('/candidates/andru-volinsky/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_anthony_eramo(self):
        response = self.client.get('/candidates/anthony-eramo/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_ben_choi(self):
        response = self.client.get('/candidates/ben-choi/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_brad_avakian(self):
        response = self.client.get('/candidates/brad-avakian/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_brian_whitecalf(self):
        response = self.client.get('/candidates/brian-whitecalf/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_brianna_lennon(self):
        response = self.client.get('/candidates/brianna-lennon/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_brittney_miller(self):
        response = self.client.get('/candidates/brittney-miller/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_carmen_yulin_cruz(self):
        response = self.client.get('/candidates/carmen-yulin-cruz/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_carol_ammons(self):
        response = self.client.get('/candidates/carol-ammons/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_charles_pelkey(self):
        response = self.client.get('/candidates/charles-pelkey/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_chase_iron_eyes(self):
        response = self.client.get('/candidates/chase-iron-eyes/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_chris_rabb(self):
        response = self.client.get('/candidates/chris-rabb/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_chris_schwartz(self):
        response = self.client.get('/candidates/chris-schwartz/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_clara_hart(self):
        response = self.client.get('/candidates/clara-hart/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_dan_quick(self):
        response = self.client.get('/candidates/dan-quick/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_david_bowen(self):
        response = self.client.get('/candidates/david-bowen/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_david_zuckerman(self):
        response = self.client.get('/candidates/david-zuckerman/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_dean_preston(self):
        response = self.client.get('/candidates/dean-preston/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_deborah_ross(self):
        response = self.client.get('/candidates/deborah-ross/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_devon_reese(self):
        response = self.client.get('/candidates/devon-reese/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_dwight_bullard(self):
        response = self.client.get('/candidates/dwight-bullard/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_elizabeth_thompson(self):
        response = self.client.get('/candidates/elizabeth-thompson/')
        self.assertEqual(response.status_code, 301)
    

    def test_candidates_elizabeth_thomson(self):
        response = self.client.get('/candidates/elizabeth-thomson/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_eloise_reyes(self):
        response = self.client.get('/candidates/eloise-reyes/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_erin_quade(self):
        response = self.client.get('/candidates/erin-quade/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_eva_bermudez(self):
        response = self.client.get('/candidates/eva-bermudez/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_gabriel_costilla(self):
        response = self.client.get('/candidates/gabriel-costilla/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_gary_kroeger(self):
        response = self.client.get('/candidates/gary-kroeger/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_greg_jones(self):
        response = self.client.get('/candidates/greg-jones/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_ilhan_omar(self):
        response = self.client.get('/candidates/ilhan-omar/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_irvin_camacho(self):
        response = self.client.get('/candidates/irvin-camacho/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_ismael_ahmed(self):
        response = self.client.get('/candidates/ismael-ahmed/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_james_eldridge(self):
        response = self.client.get('/candidates/james-eldridge/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jamie_raskin(self):
        response = self.client.get('/candidates/jamie-raskin/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jane_kim(self):
        response = self.client.get('/candidates/jane-kim/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jared_cates(self):
        response = self.client.get('/candidates/jared-cates/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jason_ritchie(self):
        response = self.client.get('/candidates/jason-ritchie/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jeanine_calkin(self):
        response = self.client.get('/candidates/jeanine-calkin/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jesse_arreguin(self):
        response = self.client.get('/candidates/jesse-arreguin/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_jonathan_brostoff(self):
        response = self.client.get('/candidates/jonathan-brostoff/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_joseph_salazar(self):
        response = self.client.get('/candidates/joseph-salazar/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_josh_elliott(self):
        response = self.client.get('/candidates/josh-elliott/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_juan_mendez(self):
        response = self.client.get('/candidates/juan-mendez/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_julie_nitsch(self):
        response = self.client.get('/candidates/julie-nitsch/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_justin_bamberg(self):
        response = self.client.get('/candidates/justin-bamberg/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_justin_wayne(self):
        response = self.client.get('/candidates/justin-wayne/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_kai_degner(self):
        response = self.client.get('/candidates/kai-degner/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_kaniela_ing(self):
        response = self.client.get('/candidates/kaniela-ing/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_kari_boiter(self):
        response = self.client.get('/candidates/kari-boiter/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_keith_ellison(self):
        response = self.client.get('/candidates/keith-ellison/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_ken_gucker(self):
        response = self.client.get('/candidates/ken-gucker/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_larry_scherer(self):
        response = self.client.get('/candidates/larry-scherer/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_lorenzo_arredondo(self):
        response = self.client.get('/candidates/lorenzo-arredondo/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_luis_ramos(self):
        response = self.client.get('/candidates/luis-ramos/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_manuel_natal(self):
        response = self.client.get('/candidates/manuel-natal/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_marcia_ranglin_vassell(self):
        response = self.client.get('/candidates/marcia-ranglin-vassell/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_marcy_kaptur(self):
        response = self.client.get('/candidates/marcy-kaptur/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_mari_cordes(self):
        response = self.client.get('/candidates/mari-cordes/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_mark_king(self):
        response = self.client.get('/candidates/mark-king/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_mark_mackenzie(self):
        response = self.client.get('/candidates/mark-mackenzie/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_martin_quezada(self):
        response = self.client.get('/candidates/martin-quezada/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_martin_quezeda(self):
        response = self.client.get('/candidates/martin-quezeda/')
        self.assertEqual(response.status_code, 301)
    

    def test_candidates_mary_keefe(self):
        response = self.client.get('/candidates/mary-keefe/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_mary_lundgren(self):
        response = self.client.get('/candidates/mary-lundgren/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_melvin_willis(self):
        response = self.client.get('/candidates/melvin-willis/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_michael_tubbs(self):
        response = self.client.get('/candidates/michael-tubbs/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_mike_connolly(self):
        response = self.client.get('/candidates/mike-connolly/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_miranda_gold(self):
        response = self.client.get('/candidates/miranda-gold/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_misty_snow(self):
        response = self.client.get('/candidates/misty-snow/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_morgan_carroll(self):
        response = self.client.get('/candidates/morgan-carroll/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_nanette_barragan(self):
        response = self.client.get('/candidates/nanette-barragan/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_nathan_morguelan(self):
        response = self.client.get('/candidates/nathan-morguelan/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_nicole_cannizzaro(self):
        response = self.client.get('/candidates/nicole-cannizzaro/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_noel_frame(self):
        response = self.client.get('/candidates/noel-frame/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_owen_carver(self):
        response = self.client.get('/candidates/owen-carver/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_pat_jehlen(self):
        response = self.client.get('/candidates/pat-jehlen/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_patricia_faye_brazel(self):
        response = self.client.get('/candidates/patricia-faye-brazel/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_paul_clements(self):
        response = self.client.get('/candidates/paul-clements/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_peter_jacob(self):
        response = self.client.get('/candidates/peter-jacob/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_pramila_jayapal(self):
        response = self.client.get('/candidates/pramila-jayapal/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_raul_grijalva(self):
        response = self.client.get('/candidates/raul-grijalva/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_rick_nolan(self):
        response = self.client.get('/candidates/rick-nolan/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_robert_cushing(self):
        response = self.client.get('/candidates/robert-cushing/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_robert_founds(self):
        response = self.client.get('/candidates/robert-founds/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_robyn_porter(self):
        response = self.client.get('/candidates/robyn-porter/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_rochelle_okimoto(self):
        response = self.client.get('/candidates/rochelle-okimoto/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_rudy_martinez(self):
        response = self.client.get('/candidates/rudy-martinez/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_russ_feingold(self):
        response = self.client.get('/candidates/russ-feingold/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_sabrina_shrader(self):
        response = self.client.get('/candidates/sabrina-shrader/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_sara_niccoli(self):
        response = self.client.get('/candidates/sara-niccoli/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_sarah_lloyd(self):
        response = self.client.get('/candidates/sarah-lloyd/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_teresa_meyer(self):
        response = self.client.get('/candidates/teresa-meyer/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_terry_alexander(self):
        response = self.client.get('/candidates/terry-alexander/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_thomas_nelson(self):
        response = self.client.get('/candidates/thomas-nelson/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_tim_ashe(self):
        response = self.client.get('/candidates/tim-ashe/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_tim_kacena(self):
        response = self.client.get('/candidates/tim-kacena/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_troy_jackson(self):
        response = self.client.get('/candidates/troy-jackson/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_tulsi_gabbard(self):
        response = self.client.get('/candidates/tulsi-gabbard/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_vernon_miller(self):
        response = self.client.get('/candidates/vernon-miller/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_victoria_leigh(self):
        response = self.client.get('/candidates/victoria-leigh/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_vincent_fort(self):
        response = self.client.get('/candidates/vincent-fort/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_wenona_benally(self):
        response = self.client.get('/candidates/wenona-benally/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_zach_dorholt(self):
        response = self.client.get('/candidates/zach-dorholt/')
        self.assertEqual(response.status_code, 200)
    

    def test_candidates_zephyr_teachout(self):
        response = self.client.get('/candidates/zephyr-teachout/')
        self.assertEqual(response.status_code, 200)
    

    def test_check_registration(self):
        response = self.client.get('/page/check-registration/')
        self.assertEqual(response.status_code, 200)


    def test_page_check_registration(self):
        response = self.client.get('/page/check-registration/')
        self.assertEqual(response.status_code, 301)

    def test_check_registration(self):
        response = self.client.get('/check-registration/')
        self.assertEqual(response.status_code, 200)


    def test_dakota_access_filmmaker(self):
        response = self.client.get('/dakota-access-filmmaker/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_(self):
        response = self.client.get('/ballot-initiatives/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_alabama_amendment_8(self):
        response = self.client.get('/ballot-initiatives/alabama-amendment-8/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_alaska_measure_1(self):
        response = self.client.get('/ballot-initiatives/alaska-measure-1/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_arkansas_issue_7(self):
        response = self.client.get('/ballot-initiatives/arkansas-issue-7/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_58(self):
        response = self.client.get('/ballot-initiatives/california-prop-58/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_59(self):
        response = self.client.get('/ballot-initiatives/california-prop-59/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_61(self):
        response = self.client.get('/ballot-initiatives/california-prop-61/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_62(self):
        response = self.client.get('/ballot-initiatives/california-prop-62/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_64(self):
        response = self.client.get('/ballot-initiatives/california-prop-64/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_66(self):
        response = self.client.get('/ballot-initiatives/california-prop-66/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_california_prop_67(self):
        response = self.client.get('/ballot-initiatives/california-prop-67/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_colorado_amendment_69(self):
        response = self.client.get('/ballot-initiatives/colorado-amendment-69/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_florida_amendment_2(self):
        response = self.client.get('/ballot-initiatives/florida-amendment-2/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_louisiana_amendment_2(self):
        response = self.client.get('/ballot-initiatives/louisiana-amendment-2/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_maine_question_1(self):
        response = self.client.get('/ballot-initiatives/maine-question-1/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_maine_question_4(self):
        response = self.client.get('/ballot-initiatives/maine-question-4/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_maine_question_5(self):
        response = self.client.get('/ballot-initiatives/maine-question-5/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_maryland_citizens_election_fund(self):
        response = self.client.get('/ballot-initiatives/maryland-citizens-election-fund/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_massachusetts_measure_2(self):
        response = self.client.get('/ballot-initiatives/massachusetts-measure-2/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_missouri_amendment_6(self):
        response = self.client.get('/ballot-initiatives/missouri-amendment-6/')
        self.assertEqual(response.status_code, 200)


    def test_initiatives_montana_initiative_182(self):
        response = self.client.get('/ballot-initiatives/montana-initiative-182/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_nebraska_bill_268(self):
        response = self.client.get('/ballot-initiatives/nebraska-bill-268/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_nevada_question_2(self):
        response = self.client.get('/ballot-initiatives/nevada-question-2/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_oklahoma_question_776(self):
        response = self.client.get('/ballot-initiatives/oklahoma-question-776/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_oregon_measure_97(self):
        response = self.client.get('/ballot-initiatives/oregon-measure-97/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_oregon_measure_98(self):
        response = self.client.get('/ballot-initiatives/oregon-measure-98/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_south_dakota_amendment_t(self):
        response = self.client.get('/ballot-initiatives/south-dakota-amendment-t/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_south_dakota_law_20(self):
        response = self.client.get('/ballot-initiatives/south-dakota-law-20/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_south_dakota_measure_22(self):
        response = self.client.get('/ballot-initiatives/south-dakota-measure-22/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_virginia_right_to_work(self):
        response = self.client.get('/ballot-initiatives/virginia-right-to-work/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_washington_initiative_1433(self):
        response = self.client.get('/ballot-initiatives/washington-initiative-1433/')
        self.assertEqual(response.status_code, 200)
    

    def test_initiatives_washington_initiative_735(self):
        response = self.client.get('/ballot-initiatives/washington-initiative-735/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues(self):
        response = self.client.get('/issues/')
        self.assertEqual(response.status_code, 200)
        

    def test_issues_a_living_wage(self):
        response = self.client.get('/issues/a-living-wage/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_affordable_housing(self):
        response = self.client.get('/issues/affordable-housing/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_aids_and_hiv(self):
        response = self.client.get('/issues/aids-and-hiv/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_big_money_in_politics(self):
        response = self.client.get('/issues/big-money-in-politics/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_caring_for_our_veterans(self):
        response = self.client.get('/issues/caring-for-our-veterans/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_climate_change(self):
        response = self.client.get('/issues/climate-change/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_college_tuition(self):
        response = self.client.get('/issues/college-tuition/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_creating_decent_paying_jobs(self):
        response = self.client.get('/issues/creating-decent-paying-jobs/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_disability_rights(self):
        response = self.client.get('/issues/disability-rights/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_empowering_tribal_nations(self):
        response = self.client.get('/issues/empowering-tribal-nations/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_foreign_policy(self):
        response = self.client.get('/issues/foreign-policy/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_immigration(self):
        response = self.client.get('/issues/immigration/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_income_inequality(self):
        response = self.client.get('/issues/income-inequality/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_lgbt_equality(self):
        response = self.client.get('/issues/lgbt-equality/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_medicare_for_all(self):
        response = self.client.get('/issues/medicare-for-all/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_prescription_drug_prices(self):
        response = self.client.get('/issues/prescription-drug-prices/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_puerto_rico(self):
        response = self.client.get('/issues/puerto-rico/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_racial_justice(self):
        response = self.client.get('/issues/racial-justice/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_strengthen_social_security(self):
        response = self.client.get('/issues/strengthen-social-security/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_tpp(self):
        response = self.client.get('/issues/tpp/')
        self.assertEqual(response.status_code, 200)
    

    def test_issues_womens_rights(self):
        response = self.client.get('/issues/womens-rights/')
        self.assertEqual(response.status_code, 200)
    

    def test_page_join_lucy_flores_support_women_leaders(self):
        response = self.client.get('/page/join-lucy-flores-support-women-leaders/')
        self.assertEqual(response.status_code, 301)

    def test_join_lucy_flores_support_women_leaders(self):
        response = self.client.get('/join-lucy-flores-support-women-leaders/')
        self.assertEqual(response.status_code, 200)


    def test_press_josh_fox_and_our_revolution_team_up(self):
        response = self.client.get('/press/josh-fox-and-our-revolution-team-up/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_announces_final_round_of_endorsements(self):
        response = self.client.get('/press/our-revolution-announces-final-round-of-endorsements/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_announces_formation_of_board(self):
        response = self.client.get('/press/our-revolution-announces-formation-of-board/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_announces_latest_round_of_endorsements(self):
        response = self.client.get('/press/our-revolution-announces-latest-round-of-endorsements/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_announces_more_endorsements(self):
        response = self.client.get('/press/our-revolution-announces-more-endorsements/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_announces_next_round_of_endorsements(self):
        response = self.client.get('/press/our-revolution-announces-next-round-of-endorsements/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_announces_second_round_of_endorsements(self):
        response = self.client.get('/press/our-revolution-announces-second-round-of-endorsements/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_on_ma_primary_wins(self):
        response = self.client.get('/press/our-revolution-on-ma-primary-wins/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_reacts_final_presidential_debate(self):
        response = self.client.get('/press/our-revolution-reacts-final-presidential-debate/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_statement_on_ri_and_ny(self):
        response = self.client.get('/press/our-revolution-statement-on-ri-and-ny/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_statement_on_shailene_woodley_arrest(self):
        response = self.client.get('/press/our-revolution-statement-on-shailene-woodley-arrest/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_statement_on_shootings(self):
        response = self.client.get('/press/our-revolution-statement-on-shootings/')
        self.assertEqual(response.status_code, 200)
    

    def test_press_our_revolution_substantive_discussion(self):
        response = self.client.get('/press/our-revolution-substantive-discussion/')
        self.assertEqual(response.status_code, 200)


    def test_founding_statement_of_our_revolution_board(self):
        response = self.client.get('/press/founding-statement-of-our-revolution-board/')
        self.assertEqual(response.status_code, 200)
    
    def test_our_revolution_stands_with_dakota_access_pipeline_protestors(self):
        response = self.client.get('/press/our-revolution-stands-with-dakota-access-pipeline-protestors')
        self.assertEqual(response.status_code, 200)

    def test_privacy_policy(self):
        response = self.client.get('/privacy-policy/')
        self.assertEqual(response.status_code, 200)
    

    def test_prop_61_toolkit(self):
        response = self.client.get('/prop-61-toolkit/')
        self.assertEqual(response.status_code, 200)
    

    def test_register_to_vote(self):
        response = self.client.get('/register-to-vote/')
        self.assertEqual(response.status_code, 200)
    

    def test_signup(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 301)
    

    def test_stop_the_tpp(self):
        response = self.client.get('/stop-the-tpp/')
        self.assertEqual(response.status_code, 301)
    

    def test_stop_tpp_now(self):
        response = self.client.get('/stop-tpp-now/')
        self.assertEqual(response.status_code, 200)
    

    def test_success(self):
        response = self.client.get('/success/')
        self.assertEqual(response.status_code, 200)
    

    def test_tpp(self):
        response = self.client.get('/tpp/')
        self.assertEqual(response.status_code, 301)
    

    def test_volunteer_signup(self):
        response = self.client.get('/volunteer-signup/')
        self.assertEqual(response.status_code, 301)
 
    def test_polling_locator(self):
        response = self.client.get('/polling-locator/')
        self.assertEqual(response.status_code, 200)
    # stage boss
    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)
    tests.utils.web_dike_reckon_boss(client) 
    
    # stage board
    tests.utils.web_dike_begin_voting_board(client)
    
    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[1], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[2], "position": POSITION_TREASURE, "rank": 1},
        {"fellow": users[3], "position": POSITION_SECRET, "rank": 1},
        {"fellow": users[4], "position": POSITION_LIBRARY, "rank": 1},
        {"fellow": users[5], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[6], "position": POSITION_FREE, "rank": 2},
        {"fellow": users[7], "position": POSITION_FREE, "rank": 3},
    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[12], "position": POSITION_TREASURE, "rank": 1},
    ])
    
    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)
    tests.utils.web_dike_reckon_board(client, [
        {"position": POSITION_VICE, "fellows": [users[11]]},
        {"position": POSITION_TREASURE, "fellows": [users[2]]},
        {"position": POSITION_SECRET, "fellows": [users[3]]},
        {"position": POSITION_LIBRARY, "fellows": [users[4]]},
        {"position": POSITION_FREE, "fellows": [users[1], users[6], users[7]]},
    ])

    # stage covision
    tests.utils.web_dike_begin_voting_covision(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[8], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[9], "position": POSITION_COVISION, "rank": 2},
        {"fellow": users[10], "position": POSITION_COVISION, "rank": 3},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)
    tests.utils.web_dike_reckon_covision(client)

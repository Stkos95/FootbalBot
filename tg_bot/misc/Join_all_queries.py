
query_tournament = '''
query frontend {
        frontend {
            tournament(tournament_id:1025285){
                tournament_id
                full_name
                short_name
                cover
                season_id
                is_published
                in_schedule
                type
                category
                rounds{
                    round_id
                    name
                }
                applications{
                    team{
                        
                    }
                    status
                    name
                }
            }

        } }

'''
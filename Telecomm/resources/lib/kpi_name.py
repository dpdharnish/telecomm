def init_timing(session_data):
    # initialising variables
    session_data.status = "Fail_launch"
    
    # Categories
    session_data.KPI_LABEL_CATEGORY = "kpi"
    
    #Add tags to this dictionary {'key': 'connection_status', 'value': 'Mobile'}
    session_data.tags = []
    
    #Data KPIs
    session_data.non_time_kpis = {
        
        
        
    }

    # KPI Labels
    session_data.kpi_labels = {
        'Launch Time':{'start':None,'end':None},  #done
        'Search Tab Load Time':{'start':None,'end':None},  #done
        'Search Time':{'start':None,'end':None},   #done
        'Game Setup Time':{'start':None,'end':None},   #done
        'Login Time':{'start':None,'end':None},     #done
        'Game Load Time':{'start':None,'end':None}, #done
        'Join Page Load Time':{'start':None,'end':None},   #done
        'Meet Join Time':{'start':None,'end':None},  #done
    }

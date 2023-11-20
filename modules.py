import pandas as pd
import numpy as np
from os.path import exists
from functools import reduce
import datetime
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")#there are some warnings that show up from pandas that don't effect us, so we just mute them

#authored by Tom Odem on 12 November 2023
#returns a numpy array of numpy arrays, where the first elements of each sub array is a daily sleep time and the proceeding elements are the activities the user 
#completed throughout the day in sequence
def get_and_dayitise_data():
 
    users_df = pd.read_csv('user_information.csv') #read the user_information.csv file to get user ids, depression scores, etc
    day_by_day = []

    #go through all users in user_information.csv
    for user in np.uniqie(users_df['user_id']): #unique so that it doesn't try to open duplicate entries
       
        if(exists('user_tags/'+str(user)+'.csv')): #if the user's tags csv exists then open it and continue
            u = pd.read_csv('user_tags/'+str(user)+'.csv')
            u = u.drop(columns=['end'])

            u['date'] = [pd.to_datetime(t).date() for t in u['start']] #add date column




            #find daily sleep time
            #finds the time the user wakes up everyday
            wakeup_time = u.loc[(u['labelName'] == 'Wake up')]
            wakeup_time['start'] = [pd.to_datetime(t)  for t in wakeup_time['start']]
            wakeup_time['date']= [pd.to_datetime(t).date() for t in wakeup_time['start']]
            wakeup_time['hour']= [pd.to_datetime(t).time() for t in wakeup_time['start']]

            #finds the time the user went to sleep everyday
            sleep_time = u.loc[(u['labelName'] == 'Sleep')]
            sleep_time['start'] = [pd.to_datetime(t) for t in sleep_time['start']]
            sleep_time['date']= [(pd.to_datetime(t)+ pd.Timedelta(days=1)).date() for t in sleep_time['start']]
            sleep_time['hour']= [pd.to_datetime(t).time() for t in sleep_time['start']]
            
            #computes the amount of time the user slept daily
            r = pd.merge(wakeup_time, sleep_time, on ='date')
            r['start_y'] = pd.to_datetime(r['start_y'])
            r['start_x'] = pd.to_datetime(r['start_x'])
            r['sleeptime'] = (-1*(r['start_y'] - r['start_x']).astype('timedelta64[m]'))/60 #find the difference between when they woke up from when they went to sleep in hours
            r = r[['sleeptime','date']].groupby('date').mean().reset_index().astype({'date':object})#we only need the date and the sleeptime, we reset the index to change it back 
                                                                                                    #to a dataframe, and we want to force teh date to be of type object so that we can always merge even if there are no entries
            
            #document the activities performed on each day
            for index, row in r.iterrows(): #for each day in the average sleep amount dataframe r
                day = row.to_numpy()[0]#get the day
                activities = u.loc[(u['date'] == day) & (u['labelName'] != 'Sleep') & (u['labelName'] != 'Wake up')] #get all of the activities that happened on this day that are not sleeping related
                activities = activities['labelName'].to_numpy() #get only the activities, as in drop every other column
                activities = np.append(row['sleeptime'],activities) #add the sleep time to the beginning of the array, so we can find it later
                activities = activities[activities != 'None'] #remove any 'None' elements from the array

                day_by_day.append(activities)#add the activities and sleep time from today to the day_by_day list


        

            

            
    
        else:
            print(f'no user_tags: {user}') #the tags csv was missing for this user


    return np.array(day_by_day) #change the list into an industry standard numpy array and return



#authored by Tom Odem on 12 November 2023
#computes the averages of data over a set increments of time for users, then merges averages with respective depression measurements
def get_and_avg_data(avg_over_n_days = 7):
#avg_over_n_days: integer value of the amount of days to compute averages over. defaults to 7, which computes weekly averages
    
    users_df = pd.read_csv('user_information.csv') #read the user_information.csv file to get user ids, depression scores, etc
    n_days_df = pd.DataFrame(columns=['user_id','avg_step','avg_sleep','avg_drink', 'avg_eat','avg_care']) #initialize the dataframe that will hold averages over n days

    #go through all users in user_information.csv
    for user in np.uniqie(users_df['user_id']):
        if(exists('user_data/data_'+str(user)+'.csv')): #if the user's data csv exists then open it and continue
            user_df = pd.read_csv('user_data/data_'+str(user)+'.csv')
            
            #find daily step count
            user_df['client_time']= [pd.to_datetime(i).date() for i in user_df['client_time']]#turn the datetime entries into just dates
            steps= user_df.groupby(['client_time'])['step'].max().reset_index().rename(columns={'client_time':'date'}).astype({'date':object})#compute the daily step count by just taking the maximum step count everyday, rename client_time to date so we can merge with others, force date to be object for merging
            
            if(exists('user_tags/'+str(user)+'.csv')): #if the user's tags csv exists then open it and continue
                u = pd.read_csv('user_tags/'+str(user)+'.csv')
                u = u.drop(columns=['end'])


                #find daily sleep time
                #finds the time the user wakes up everyday
                wakeup_time = u.loc[(u['labelName'] == 'Wake up')]
                wakeup_time['start'] = [pd.to_datetime(t)  for t in wakeup_time['start']]
                wakeup_time['date']= [pd.to_datetime(t).date() for t in wakeup_time['start']]
                wakeup_time['hour']= [pd.to_datetime(t).time() for t in wakeup_time['start']]

                #finds the time the user went to sleep everyday
                sleep_time = u.loc[(u['labelName'] == 'Sleep')]
                sleep_time['start'] = [pd.to_datetime(t) for t in sleep_time['start']]
                sleep_time['date']= [(pd.to_datetime(t)+ pd.Timedelta(days=1)).date() for t in sleep_time['start']]
                sleep_time['hour']= [pd.to_datetime(t).time() for t in sleep_time['start']]
                
                #computes the amount of time the user slept daily
                r = pd.merge(wakeup_time, sleep_time, on ='date')
                r['start_y'] = pd.to_datetime(r['start_y'])
                r['start_x'] = pd.to_datetime(r['start_x'])
                r['sleeptime'] = (-1*(r['start_y'] - r['start_x']).astype('timedelta64[m]'))/60 #find the difference between when they woke up from when they went to sleep in hours
                r = r[['sleeptime','date']].groupby('date').mean().reset_index().astype({'date':object})#we only need the date and the sleeptime, we rest the index to change it back 
                                                                                                        #to a dataframe, and we want to force teh date to be of type object so that we can always merge even if there are no entries
                
                #find daily number of times the user drank
                drinktime = u.loc[(u['labelName'] == 'Drink')] #we only want the entries that correlate to drinking
                drinktime['date'] = [pd.to_datetime(t).date() for t in drinktime['start']] #gives us the date that the drink happened, since we do not need to know the exact time
                drinktime = drinktime.rename(columns={'labelName':'drinktime'}).groupby('date').count().drop(['start'], axis = 1).reset_index().astype({'date':object}) #finds the number of times the user drank a day by grouping by the date, we drop start becase
                                                                                                                                                                        #we only need to know the date, we reset the index to turn it back into a dataframe, and we force date to be object for merging
                
                #find daily number of times the user ate
                eattime = u.loc[(u['labelName'] == 'Eat')] #we only want the entries that correlate to eating
                eattime['date'] = [pd.to_datetime(t).date() for t in eattime['start']] #gives us the date that the eat happened, since we do not need to know the exact time
                eattime = eattime.rename(columns={'labelName':'eattime'}).groupby('date').count().drop(['start'], axis = 1).reset_index().astype({'date':object}) #finds the number of times the user ate a day by grouping by the date, we drop start becase
                                                                                                                                                                #we only need to know the date, we reset the index to turn it back into a dataframe, and we force date to be object for merging
                
                #find daily number of times the user performed and act of self care
                self_care = u.loc[(u['labelName'] == 'Take shower') | (u['labelName'] == 'Go to bathroom')] #we only want the entries that correlate to self care
                self_care['date'] = [pd.to_datetime(t).date() for t in self_care['start']] #gives us the date that the self care happened, since we do not need to know the exact time
                self_care = self_care.rename(columns={'labelName':'selfcare'}).groupby('date').count().drop(['start'], axis = 1).reset_index().astype({'date':object}) #finds the number of times the user self cared a day by grouping by the date, we drop start becase
                                                                                                                                                                        #we only need to know the date, we reset the index to turn it back into a dataframe, and we force date to be object for merging

                #merge all of the daily counts on time
                data_frames = [r,drinktime,eattime,self_care,steps] #the dataframes to be merged
                data_by_day_df = reduce(lambda  left,right: pd.merge(left,right,on=['date'],how='outer'), data_frames) #pd.merge can only merge two at a time, so we have to run merge over all of the dataframes

                max_date = data_by_day_df['date'].max() #find the latest date in the dataframe

                current_date = data_by_day_df['date'].min() #we start at the earliest date in the dataframe

                
                #take averages over avg_over_n_days incriments from the first day to the last day
                while current_date < max_date: #while we haven't reached the last day
                    n_days_from_current_date = current_date+datetime.timedelta(days=avg_over_n_days) #find the day that is avg_over_n_days away from the current date

                    range = (data_by_day_df['date'] >= current_date) & (data_by_day_df['date'] < n_days_from_current_date) #define the range of dates we select from data_by_day_df 

                    #compute the averages of each activity within the given range
                    avg_sleep = np.mean(data_by_day_df.loc[range]['sleeptime'])
                    avg_drink = np.mean(data_by_day_df.loc[range]['drinktime'])
                    avg_eat = np.mean(data_by_day_df.loc[range]['eattime'])
                    avg_care = np.mean(data_by_day_df.loc[range]['selfcare'])
                    avg_step = np.mean(data_by_day_df.loc[range]['step'])

                    #add the averages to predic_df
                    temp = pd.DataFrame([[user,avg_step, avg_sleep, avg_drink, avg_eat, avg_care]], columns=['user_id','avg_step','avg_sleep','avg_drink', 'avg_eat', 'avg_care'])
                    n_days_df = pd.concat([n_days_df, temp])


                    current_date = n_days_from_current_date #our range did not include the day avg_over_n_days away, so that day is now our current day to start from


                

                
        
            else:
                print(f'no user_tags: {user}') #the tags csv was missing for this user
        else:
            print(f'no user_data: {user}') #the data csv was missing for this user


    averages_df = pd.merge(n_days_df, users_df[['user_id','depression_class', 'depression_score']], on='user_id').set_index('user_id') #merge the averages with their respective depression class and deppression score
    return averages_df

#authored by Tom Odem on 18 November 2023

#given a number, a mean, and an std, categorize the number based on if it is within one std of the mean
def categorize_based_on_std(num, mean, std):
    if num > mean+std: #it is outstide the average range on the high end
        return 2
    if num > mean-std and num < mean+std: #it is within average range
        return 1
    return 0 #it is outside the average range on the low end


#turns a column's values into values 0, 1, or 2 based on if the value is within one std of the column mean
def categorize_column(col):
    col_name = col.name #record the name of the column
    col = col.to_numpy() #change it to numpy so we can see it
    mean = np.nanmean(col) #find mean
    std = np.nanstd(col) #find std
    for i in range(len(col)): #replace values with categories based on if the values are within one std of mean
        col[i] = categorize_based_on_std(col[i], mean, std)
        
    return pd.Series(col, name=col_name) #change the new categorized values array into a series with its name then return it

import os
import pandas as pd
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "C:\\Users\\hanse\\Desktop\\FlaskIntroduction\\static\\files"

@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if request.files :
            date = request.form['date']
            time = request.form['time']

            print('DateTime' + str(date) + str(time))

            csv = request.files['file']
            csv.save(os.path.join(app.config['UPLOAD_FOLDER'], csv.filename))

            csv2 = request.files['file2']
            csv2.save(os.path.join(app.config['UPLOAD_FOLDER'], csv2.filename))

            dataFrame = proccess(os.path.join(app.config['UPLOAD_FOLDER'], csv.filename), 
                                 os.path.join(app.config['UPLOAD_FOLDER'], csv2.filename), 
                                 date, time) 

            return render_template('data.html', data = dataFrame.to_html())
        else:
            print('no file')

        return redirect(request.url)
    return """
            <form method='post' action='/' enctype='multipart/form-data'>
                Upload class name list and attendance: <br/>
                <br/>
                <label for="NameList">NameList:</label><br/>
                <input type='file' name='file' id="file"><br/>
                <br/>
                <label for="AttendanceList">NameAttendance:</label><br/>
                <input type="file" name="file2" id="file2">
                <br/><br/><br/>
                <input type="date" id="date" name="date" value="2021-09-22" min="2021-01-01" max="2022-12-31">
                <input type="time" id="time" name="time"><br/>
                <br/><br/>
                <input type='submit' value='Upload'>
            </form>
           """


def proccess(_name_data, _student_data, date, time):
    name_data = pd.read_csv(_name_data, encoding = 'utf-16', sep='\t')
    student_data = pd.read_csv(_student_data, encoding = 'utf-16', sep='\t')

    print(date + " : " + '2021-05-17')

    lessonStartDate = date
    lessonStartTime = time
    lessonStartDateTime = lessonStartDate + ' ' + lessonStartTime

    df_name = pd.DataFrame(name_data);
    df = pd.DataFrame(student_data);

    df_name['Time'] = ""
    df_name['Late by'] = ""
    df_name['Penalty'] = ""

    df['Timestamp'] = df['Timestamp'].apply(lambda x: pd.Timestamp(x).strftime('%d-%B-%Y %I:%M:%S %p'))
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    nameList = df['Full Name'].unique()

    data = []

    for name in nameList:
        timeList = df.loc[(df['Full Name'] == name) & (df['User Action'] == 'Joined')]
        
        startTime = pd.to_datetime(lessonStartDateTime)
        timeDiff = timeList['Timestamp'].min() - startTime
        timeDiff = timeDiff.total_seconds()
        
        lateBy = 0
        
        if timeDiff > 120 * 60:
            lateBy = 3
        elif timeDiff > 90 * 60:
            lateBy = 2
        elif timeDiff > 30 * 60: 
            lateBy = 1
        else:
            lateBy = 0
        
        minTime = str(timeList['Timestamp'].min())
        #print(name[:15] + "\t" + minTime + "\t" + str(lateBy))
        
        #timeDiff = str(datetime.timedelta(seconds=timeDiff))
        
        hrs = int(timeDiff/(60*60))
        mins =  abs(int(timeDiff/60) - (hrs*60))
        secs = int(timeDiff%60)
        
        if timeDiff < 0 :
            sign = '-'
        else:
            sign = '+'
        
        
        if hrs < 10 :
            hrs = "0" + str(hrs)
        else:
            hrs = str(hrs)
        
        if mins < 10 :
            mins = "0" + str(mins)
        else:
            mins = str(mins)
            
        if secs < 10 :
            secs = "0" + str(secs)
        else:
            secs = str(secs)
        
        lateByStr = sign + str(hrs) + ":" + mins + ":" + secs
        
        data.append([name, minTime, lateByStr, lateBy])
        df2 = pd.DataFrame(data, columns=['Name', 'Time', 'Late by' ,'Penalty'])

    print('Total Student: ' + str(len(nameList)))
    df2

    nameIndex = 0

    for name in df_name['Name']:
        df_name['Time'][nameIndex] = 'Absent'
        df_name['Late by'][nameIndex] = 'Absent'
        df_name['Penalty'][nameIndex] = 0
        attendanceIndex = 0
        
        for attendanceName in df2['Name']:
            if name == attendanceName:
                df_name['Time'][nameIndex] = df2['Time'][attendanceIndex]
                df_name['Late by'][nameIndex] = df2['Late by'][attendanceIndex]
                df_name['Penalty'][nameIndex] = str(df2['Penalty'][attendanceIndex])
                break
            else:
                attendanceIndex+=1
        
        nameIndex += 1

    return df_name    
    print(df_name)

if __name__ == '__main__':
    app.debug = True
    app.run()
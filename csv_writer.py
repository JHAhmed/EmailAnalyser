import csv

def write_csv(customer, analysis, filepath):

    customer_name = customer

    # name of csv file
    filename = f"{filepath}/{customer_name}_sentiment.csv"

    # field names
    fields = ['Date', 'Subject', 'Rating']
    
    # data rows of csv file
    rows = analysis

    # rows.append(analysis)
    # if 

    # writing to csv file
    with open(filename, 'a') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(fields)
        
        # writing the data rows
        csvwriter.writerows(rows)
        

import os, io, sys, math, json, random
import pandas as pd
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from itertools import permutations
from queue import Queue


class Subject:
    def __init__(self, year, div, code, name, type, teachers,l,t,p):
        self.year = year
        self.div = div
        self.code = code
        self.name = name
        self.type = type
        self.teachers = teachers
        self.l = l
        self.t = t
        self.p = p

class Teacher:
    def __init__(self, name, tt_matrix):
        self.name = name
        self.tt_matrix = tt_matrix

all_teachers = []
all_subjects = []
lab_subjects = []
year_iter = 0

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]    

def get_empty_tt():
    return [[None]*8 for _ in range(5)]

ttA = [get_empty_tt(), get_empty_tt(), get_empty_tt(), get_empty_tt()]
ttB = [get_empty_tt(), get_empty_tt(), get_empty_tt(), get_empty_tt()]
ttL = get_empty_tt()

def upload_file(request):
    global year_iter
    output_file_path = '/path/to/output/file.csv'
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded Excel file
            excel_file = form.cleaned_data['file']

            # Convert Excel to CSV
            df = pd.read_excel(excel_file)
            filtered_df = df[df.iloc[:, 1].isin(years[year_iter])]

            csv_data = filtered_df.to_csv(index=False)
            print(csv_data)

            makeTT(csv_data)
            

            # Perform operations on CSV data
            # processed_data = process_file(excel_file)

            # Convert processed data back to CSV
            # processed_csv_data = processed_data.to_csv(index=False)

            # # Save the processed CSV data to the 'output' folder
            # output_folder = 'output'
            # os.makedirs(output_folder, exist_ok=True)
            # output_file_path = os.path.join(output_folder, 'output_file.csv')
            # processed_data.to_csv(output_file_path, index=False)

            # Render a response or redirect to another page
            # return render(request, 'success.html', {'output_file_path': output_file_path})

            year_iter = year_iter + 1
            return render(request, 'upload_file.html', {'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'upload_file.html', {'form': form})

def line_break(s):
    n = 15
    print('#'*n + ' ' + s + ' ' + '#'*n)

def upload_teachers(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['file']
            df = pd.read_csv(csv_file)
            print(df)
            
            global all_teachers
            names = []

            for ele in df:
                names.append(ele)

            print(names)

            # Create Teacher objects with initial tt_matrix containing null values
            if (len(all_teachers) == 0):
                all_teachers = [Teacher(name, [[None]*8 for _ in range(5)]) for name in names]

            # return render(request, 'upload_subjects.html', {'form': form})
            return redirect('subjects')
    else:
        form = UploadFileForm()
    return render(request, 'upload_teachers.html', {'form': form})

def upload_subjects(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['file']
            df = pd.read_csv(csv_file)
            df.head()

            global all_subjects
            global lab_subjects
            for index, row in df.iterrows():
                code = row['CODE']
                name = row['NAME']
                year = row['YEAR']
                type = row['TYPE']
                l = row['L']
                t = row['T']
                p = row['P']
                
                subject = Subject(year, 'A', code, name, type, [], l,t,p)
                all_subjects.append(subject)
                if(p == 2):
                    labA = Subject(year, 'A', code, name, type, [], l,t,p)
                    labB = Subject(year, 'B', code, name, type, [], l,t,p)
                    lab_subjects.append(labA)
                    lab_subjects.append(labB)

                if type == 0:
                    subject2 = Subject(year, 'B', code, name, type, [], l,t,p)
                    all_subjects.append(subject2)
                

            line_break('All Subjects')
            print_all_subjects(all_subjects)
            line_break('Lab Subjects')
            print_all_subjects(lab_subjects)

            return redirect('assign_teachers')
    else:
        form = UploadFileForm()
    return render(request, 'upload_subjects.html', {'form': form})

def assign_teachers_util(dictionary):
    global all_subjects
    global all_teachers

    for subject in all_subjects:
        subject.teachers.clear()

    for key, values in dictionary.items():
        print(key, values)
        for t in values:
            for teacher in all_teachers:
                if t == teacher.name:
                    all_subjects[key].teachers.append(teacher)
    line_break("assigned_teachers")
    print_all_subjects(all_subjects)

def lab_assign_teachers_util(dictionary):
    global lab_subjects
    global all_teachers

    for subject in lab_subjects:
        subject.teachers.clear()

    for key, values in dictionary.items():  
        print(key, values)
        for t in values:
            for teacher in all_teachers:
                if t == teacher.name:
                    lab_subjects[key].teachers.append(teacher)
    line_break("assigned_lab_teachers")
    print_all_subjects(lab_subjects)

def assign_teachers(request):
    if request.method == 'POST':
        
        data = request.POST
        result_dict = {}
        # lab_result_dict = {}
        key_text = 'additional_field_'
        # key_text_lab = 'lab_additional_field_' 
        extra_str = 'Delete'
        
        non_empty_values = []
        # lab_non_empty_values = []

        for key, values in data.lists():
            # if key.startswith(key_text):
            non_empty_values = [value for value in values[1:] if value]
            # elif key.startswith(key_text_lab):
            #     lab_non_empty_values = [value for value in values[1:] if value]
            
            if non_empty_values:
                # Parse the first non-empty value as JSON
                # if key.startswith(key_text):
                cleaned_key = int(key[len(key_text):]) - 1
                
                try:
                    tl = json.loads(non_empty_values[0])
                    # If the parsed value is a list, print each item separately
                    if isinstance(tl, list):
                        cleaned_values = [item.replace(extra_str, '') for item in tl]
                        print(f"{cleaned_key}: {cleaned_values}")
                        result_dict[cleaned_key] = cleaned_values

                except json.JSONDecodeError:
                    pass
                
            # elif lab_non_empty_values:
            #     # Parse the first non-empty value as JSON
            #     if key.startswith(key_text_lab):
            #         cleaned_key_lab = int(key[len(key_text_lab):]) - 1
            
            #     try:
            #         tl = json.loads(lab_non_empty_values[0])
                    
            #         # If the parsed value is a list, print each item separately
            #         if isinstance(tl, list):
            #             cleaned_values_lab = [item.replace(extra_str, '') for item in tl]
            #             print(f"{cleaned_key_lab}: {cleaned_values_lab}")
            #             lab_result_dict[cleaned_key_lab] = cleaned_values_lab

            #     except json.JSONDecodeError:
            #         pass
                
        print(result_dict)
        # print(lab_result_dict)
        assign_teachers_util(result_dict)
        # lab_assign_teachers_util(lab_result_dict)
        makeTT()
        # makeLabTT()

        print_all_teachers()

        return redirect('assign_lab')
    
    return render(request, 'assign_teachers.html', {'sub_list': all_subjects,'lab_sub_list': lab_subjects, 'all_teachers': all_teachers})

def assign_lab(request):
    if request.method == 'POST':
        
        data = request.POST
        result_dict = {}
        lab_result_dict = {}
        key_text_lab = 'lab_additional_field_' 
        extra_str = 'Delete'
        
        lab_non_empty_values = []

        for key, values in data.lists():
            lab_non_empty_values = [value for value in values[1:] if value]
                
            if lab_non_empty_values:
                # Parse the first non-empty value as JSON
                if key.startswith(key_text_lab):
                    cleaned_key_lab = int(key[len(key_text_lab):]) - 1
            
                try:
                    tl = json.loads(lab_non_empty_values[0])
                    
                    # If the parsed value is a list, print each item separately
                    if isinstance(tl, list):
                        cleaned_values_lab = [item.replace(extra_str, '') for item in tl]
                        print(f"{cleaned_key_lab}: {cleaned_values_lab}")
                        lab_result_dict[cleaned_key_lab] = cleaned_values_lab

                except json.JSONDecodeError:
                    pass
                
        print(lab_result_dict)
        lab_assign_teachers_util(lab_result_dict)
        makeLabTT()

        print_all_teachers()

        return redirect('results')
    
    return render(request, 'assign_lab.html', {'lab_sub_list': lab_subjects, 'all_teachers': all_teachers})

def print_tt(div):
    for row in div:
        for cell in row:
            if cell is None:
                print('None | ', end='')
            else:
                # print(cell)
                sub = list(cell.keys())[0]
                print(f"{sub.code + ' | '}", end='')
        print()
    print()

def print_tt_clean(div):
    for row in div:
        for cell in row:
            print(cell + ' | ')
        print()
    print()
    

def print_all_teachers():
    for teacher in all_teachers:
        print(teacher.name)
        for row in teacher.tt_matrix:
            for cell in row:
                if cell is None:
                    print('None | ', end='')
                else:
                    # print(cell)
                    sub = list(cell.keys())[0]
                    div = 'A' if cell.get(sub) == 0 else 'B'
                    print(f"{sub.code + ':' + div + ' | '}", end='')
            print()
        print()

    return

def get_all_subjects(csv_data):
    global all_teachers
    all_subjects = []

    # Convert the CSV data string to a DataFrame
    df = pd.read_csv(io.StringIO(csv_data))

    for index, row in df.iterrows():
        code = row.iloc[3]
        name = row.iloc[2]
        teachers = []

        begin = 13
        # Iterate through columns starting from index begin to the last
        print(name)
        for col_index, value in enumerate(row.iloc[begin:len(all_teachers) * 3]):
            # print(f'{col_index} : {value}')
            if pd.notna(value) and col_index % 3 == 0:
                int_val = int(value)
                if (int_val != 0):
                    print(f'{col_index} : {int_val}')
                    teachers.extend([all_teachers[col_index // 3]] * int_val)

        # Create a Subject instance and add it to the subjects list
        subject = Subject(code, name, teachers)
        all_subjects.append(subject)

    return all_subjects

def separate_subjects(all_subjects):
    divA_subs = []
    divB_subs = []
    ce_subs = []

    i = 0
    while i < len(all_subjects):
        sub = all_subjects[i]
        if 'elective' in sub.name.lower():
            i = i + 1
            sub2 = all_subjects[i]
            ce_subs.append({sub : sub2})
        elif i % 2 == 0:
            divA_subs.append(sub)
        else:
            divB_subs.append(sub)
        
        i = i + 1

    while len(ce_subs) > 2:
        ce_subs.pop()

    print('#'*20 + ' Core Electives ' + '#'*20)
    for ele in ce_subs:
        sub1 = list(ele.keys())[0]
        sub2 = ele.get(sub1)
        print(f"{sub1.code + ' :: ' + sub2.code}")

    return divA_subs, divB_subs, ce_subs

def print_all_subjects(all_subjects):
    for subject in all_subjects:
        print(f'{subject.year} : {subject.code} | {subject.name}')
        print('Teachers:')
        if subject.teachers:
            for teacher in subject.teachers:
                print(teacher.name)
    return

###### THE ALGORITHM ######

def getLoc(cat, j):
    # i = (i - j) mod 5
    i = ord(cat) - ord('A')
    i = i - j 
    if i < 0:
        i = i + 5 
    
    return i

def assignSub(sub, cat, div, delta):
    i = []

    for j in range(4):
        i.append(getLoc(cat, j))

    all_tq = Queue()
    for perm in permutations(sub.teachers):
        all_tq.put(list(perm))

    for k in range(all_tq.qsize()):
        tq_list = all_tq.get()
        tq = Queue()
        for ele in tq_list:
            tq.put(ele)

        result = assignSub2Teacher(sub, tq, i, 0, div, delta)
        if result is True:
            return True

    return False

def greenFlag(i, j, teacher, div):
    return (div[i[j]][j] is None and teacher.tt_matrix[i[j]][j] is None)

def assignSub2Teacher(sub, tq, i, j, div, delta):
    # base case
    if tq.empty():
        return True
    
    if j >= 4:
        return False

    teacher = tq.get()
    assigned = False
    if (greenFlag(i, j, teacher, div)):
        teacher.tt_matrix[i[j]][j] = {sub : delta}
        div[i[j]][j] = {sub : teacher}
        assigned = assignSub2Teacher(sub, tq, i, j+1, div, delta)
        if assigned is False:
            teacher.tt_matrix[i[j]][j] = None
            div[i[j]][j] = None

    return assigned

def flushAll(perm, k, div):
    while k >= 0:
        cat = perm[k]
        i = []
        for j in range(4):
            i.append(getLoc(cat, j))

        for j in range(4):
            if div[i[j]][j] is not None:
                sub = list(div[i[j]][j].keys())[0]
                teacher = div[i[j]][j].get(sub)
                div[i[j]][j] = None
                teacher.tt_matrix[i[j]][j] = None
        
        k = k-1

def separate_year(year):
    global all_subjects
    subs = []
    for subject in all_subjects:
        if subject.year == year:
            subs.append(subject)
    return subs

def makeTTutil(subs):
    divA_subs, divB_subs, ce_subs = separate_subjects(subs)

    line_break(f"{str(4 - year_iter) + ' Div A subjects'}")
    print_all_subjects(divA_subs)
    line_break(f"{str(4 - year_iter) + ' Div B subjects'}")
    print_all_subjects(divB_subs)

    cats = assignCE_Cat(ce_subs, ttA[year_iter], ttB[year_iter])
    line_break(f"{str(4 - year_iter) + ' Div A after Core Electives'}")
    print_tt(ttA[year_iter])
    line_break(f"{str(4 - year_iter) + ' Div B after Core Electives'}")
    print_tt(ttB[year_iter])

    assignCat(divA_subs, cats, ttA[year_iter], 0)
    line_break(f"{str(4 - year_iter) + ' Div A Final'}")
    print_tt(ttA[year_iter])

    assignCat(divB_subs, cats, ttB[year_iter], 1)
    line_break(f"{str(4 - year_iter) + ' Div B Final'}")
    print_tt(ttB[year_iter])

def makeTT():
    global year_iter

    while (year_iter < 4):
        subs = separate_year(4 - year_iter)
        makeTTutil(subs)
        year_iter = year_iter + 1
        
    year_iter = 0

def assignCE_Cat(ce_subs, divA, divB):
    n = int(len(ce_subs) / 2)
    all_cats = ['A', 'B', 'C', 'D', 'E']

    if n == 0:
        return all_cats
    
    rem_cats = []
    all_perms = Queue()
    for perm in permutations(all_cats):
        all_perms.put(list(perm))

    while not all_perms.empty():
        perm = all_perms.get()

        assigned1 = False
        assigned2 = False
        k = 0
        while k < len(ce_subs):
            pair = ce_subs[k]
            sub1 = list(pair.keys())[0]
            sub2 = pair[sub1]
            assigned1 = assignSub(sub1, perm[k], divA, 0)
            assigned2 = assignSub(sub2, perm[k], divB, 1)
            if (assigned1 and assigned2) is False:
                flushAll(perm, k, divA)
                flushAll(perm, k, divB)
                break
            k = k + 1
        
        if (assigned1 and assigned2) is True:
            rem_cats = perm[n+1:]
            break
    
    return rem_cats

def assignCat(subs, cats, div, delta):
    all_perms = Queue()
    k = 0
    for perm in permutations(cats):
        all_perms.put(list(perm))

    while not all_perms.empty():
        perm = all_perms.get()

        assigned = False
        k = 0
        while k < len(subs):
            assigned = assignSub(subs[k], perm[k], div, delta)
            if assigned is False:
                flushAll(perm, k, div)
                break
            k = k + 1
        
        if assigned is True:
            break

def next_loc(x, y):
    if x > 4:
        return 5, 8
    
    if x == 4 and y >= 7:
        return 5, 8

    if y >= 7:
        return x+1, 4
    
    return x, y+1

def get_pair(y):
    if y == 4:
        return 5
    elif y == 5:
        return 4
    elif y == 6:
        return 7
    return 6

def lab_allowed(x, y, sub):
    global ttL

    if ttL[x][y] is not None:
        return False
    
    y2 = get_pair(y)
    if ttL[x][y2] == sub:
        return False
    
    # handle teacher
    teacher = sub.teachers[0]
    if (teacher.tt_matrix[x][y] is not None) or (teacher.tt_matrix[x][y2] is not None):
        return False

    return True

def assign_lab_sub(sub,p,q):
    if sub.teachers is None:
        return
    
    global ttL
    x, y = p, q
    assigned = False
    while x < 5 and y < 8:
        if lab_allowed(x, y, sub):
            delta = 0
            if sub.div == 'B':
                delta = 1

            ttL[x][y] = sub
            teacher = sub.teachers[0]
            teacher.tt_matrix[x][y] = {sub : delta}
            y2 = get_pair(y)
            teacher.tt_matrix[x][y2] = {sub : delta}
            assigned = True
            break
        
        x, y = next_loc(x, y)
    if assigned is False:
        return assign_lab_sub(sub,0,4)
    
    return assigned, x, y

def settle_lab_subjects():
    global ttL
    global ttA
    global ttB
    
    x, y = 0, 4
    while x < 5 and y < 8:
        if ttL[x][y] is None:
            x, y = next_loc(x, y)
            continue

        sub = ttL[x][y]
        teacher = sub.teachers[0]
        year = sub.year
        div = sub.div
        tt = ttA[4 - year]
        if div == 'B':
            tt = ttB[4 - year]
        
        y2 = get_pair(y)
        tt[x][y] = {sub : teacher}
        tt[x][y2] = {sub : teacher}

        x, y = next_loc(x, y)
        

def makeLabTT():
    global lab_subjects
    global ttL
    
    for tt in ttA:
        clear_lab_tt(tt)
    
    for tt in ttB:
        clear_lab_tt(tt)
        
    for teacher in all_teachers:
        clear_lab_tt(teacher.tt_matrix)
        
    
    clear_lab_tt(ttL)
    # random.shuffle(lab_subjects)
    # ttL.clear()
    p = 0
    q = 4
    for sub in lab_subjects:
        if len(sub.teachers) > 0:
            assigned,p,q = assign_lab_sub(sub,p,q)
            print(sub.code, ' : ', assigned)
    
    settle_lab_subjects()

    line_break(' Lab ')
    print_lab_tt()

def print_lab_tt():
    global ttL
    for row in ttL:
        for cell in row:
            if cell is None:
                print('None | ', end='')
            else:
                print(f"{cell.code + ' : ' + str(cell.year) + cell.div + ' | '}", end='')
        print()
    print()
    
def flushEve():
        
    ttA.clear()
    ttB.clear()
    ttL.clear()
    
    for sub in all_subjects:
        sub.teachers.clear()
    
    for sub in lab_subjects:
        sub.teachers.clear()
        
    for teacher in all_teachers:
        teacher.tt_matrix.clear()
        teacher.tt_matrix = [[None]*8 for _ in range(5)]
        
def clear_lab_tt(tt):
    x,y = 0,4
    while x < 5 and y < 8:
        tt[x][y] = None
        x,y = next_loc(x,y)
    
def show_results(request):
    ttA_reversed = reversed(ttA)
    ttB_reversed = reversed(ttB)
    days = ["Monday","Tuesday", "Wednesday", "Thursday", "Friday"]
    teachers = all_teachers
    
    return render(request, 'show_results.html', {'ttA': ttA_reversed, 'ttB': ttB_reversed, 'all_teachers': teachers, "days":days})

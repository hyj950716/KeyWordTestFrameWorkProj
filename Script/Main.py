from Util.Excel import Excel
from Config.ProjVar import *
from KeyWord.KeyWord import *
from Util.Log import  *
import traceback
from Util.TakePic import *
from Util.TimeUtil import *
from Util.ParseConfigurationFile import *

def execute_test_steps(test_step_sheet_name,test_result_sheet_name,head_line_flag=True):
    test_result = "成功"
    pc = ParseConfigFile()
    global wb
    wb.set_sheet_by_name(test_step_sheet_name)
    test_step_data = wb.get_all_rows_values()
    wb.set_sheet_by_name(test_result_sheet_name)
    if head_line_flag:
        wb.write_line(test_step_data[0], background_color="008000")  # 写一个表头
    for row_no in range(1, len(test_step_data)):
        key_word = test_step_data[row_no][keyword_col_no]
        locator_xpath_exp = test_step_data[row_no][locator_xpath_exp_col_no]
        if isinstance(locator_xpath_exp,str)  and  "||" in locator_xpath_exp :
            section_name = locator_xpath_exp.split("||")[0]
            element_name = locator_xpath_exp.split("||")[1]
            try:
                locator_xpath_exp = pc.get_option_value(section_name,element_name)
            except Exception as e:
                info("%s %s %s" %(section_name,element_name,"没有读取到对应的定位表达式"))
        value = test_step_data[row_no][value_col_no]
        if "$define" in key_word:
            test_step_result = execute_test_steps(locator_xpath_exp, value,head_line_flag=False)
            test_step_data[row_no][test_step_execute_result_col_no] = test_step_result
            continue
        # print(key_word,locator_xpath_exp,value)
        print("--------------------------------------------")

        # 情况1：func()
        if locator_xpath_exp is None and value is None:
            command = key_word + "()"
        # 情况2：func(arg1)
        elif locator_xpath_exp is None or value is None:
            if locator_xpath_exp is not None:
                command = key_word + '("%s")' % locator_xpath_exp
            else:
                command = key_word + '("%s")' % value
        # 情况3：func(arg1,arg2)
        else:
            command = key_word + '("%s","%s")' % (locator_xpath_exp, value)

        print(command)
        try:
            test_step_data[row_no][executed_time_col_no] = get_date_time()
            if "open_browser" in command:
                driver = eval(command)
            else:
                eval(command)
            test_step_data[row_no][test_step_execute_result_col_no] = "成功"
        except Exception as e:
            test_result = "失败"
            test_step_data[row_no][test_step_execute_result_col_no] = "失败"
            test_step_data[row_no][exception_info_col_no] = traceback.format_exc()
            pic_path = take_screenshot(driver)
            test_step_data[row_no][exception_screen_shot_path_col_no] = pic_path
            info("测试步骤：" + command)
            info("异常信息：" + traceback.format_exc())
        wb.write_line(test_step_data[row_no])
    wb.save()
    return test_result

wb = Excel(test_data_file_path )
wb.set_sheet_by_name("测试用例")
test_cases = wb.get_all_rows_values()

for row_no in range(1,len(test_cases)):
    #读出测试用例是否执行的标志位
    test_case_if_executed_flag = test_cases[row_no][test_case_if_executed_flag_col_no]
    if "y" not in test_case_if_executed_flag.lower():
        continue
    #读出测试步骤的所在sheet名称
    test_step_sheet_name = test_cases[row_no][test_step_sheet_name_col_no]
    #读出测试结果的所在sheet名称
    test_result_sheet_name = test_cases[row_no][test_result_sheet_name_col_no]

    #获取当前时间，写入到当前测试用例行中的测试时间单元格
    test_cases[row_no][test_executed_time_col_no]=get_date_time()
    # 执行测试步骤所在sheet中的所有步骤，并获取测试的执行结果
    test_result = execute_test_steps(test_step_sheet_name,test_result_sheet_name)
    #写入到当前测试用例行中的测试结果单元格
    test_cases[row_no][test_result_col_no]=test_result
    #设定要操作的sheet名称
    wb.set_sheet_by_name("测试结果")
    #写入测试用例sheet的表头
    wb.write_line(test_cases[0],background_color="018000")
    #写入当前测试用例行的所有内容到测试结果sheet中
    wb.write_line(test_cases[row_no])








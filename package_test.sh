#!/bin/sh

mv lambda_function.py lambda_function_prod.py
cp lambda_function_test.py lambda_function.py
zip WindUpdateTest.zip WindUpdateTest.yaml lambda_function.py winds_lib.py fetch_data_lib.py winds_ee_lib.py 
mv lambda_function_prod.py lambda_function.py 

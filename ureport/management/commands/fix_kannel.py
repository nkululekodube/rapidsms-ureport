from django.core.management.base import BaseCommand
import traceback
import os
from script.models import ScriptSession
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
from unregister.models import Blacklist
from django.conf import settings
from rapidsms_httprouter.models import Message
from django.db import connection
from optparse import OptionParser, make_option
import re


class Command(BaseCommand):


    def handle(self, **options):

        poll =Poll.objects.get(pk=236)
        file1=open("/home/mossplix/log_8.txt")
        file2=open("/home/mossplix/log_9.txt")
        files=[file1,file2]
        num=re.compile('([0-9]+)')
        for file in files:
            lines=file.readlines()
            for line in lines:
                parts=line.strip().rsplit('[FID:]')[1].split('] [')
                identity=num.search(parts[0]).groups()[0]
                message_text=parts[3].rsplit(':')[-1]
                msg=Message.objects.filter(connection__identity=identity,text=message_text,direction="I")
                if msg.exists:
                    continue
                else:
                    msg=Message.objects.create(connection__identity=identity,text=message_text,direction="I")
                    print "created "+msg.text
                    poll.process_response(msg)


        if poll.responses.exists():
            responses=poll.responses.all()
            response_data_list=[]
            excel_file_path = os.path.join(os.path.join(os.path.join(UREPORT_ROOT,'static'),'spreadsheets'),'poll_%d.xls'%poll.pk)
            for response in responses:

                response_export_data = SortedDict()
                if response.contact and response.contact.name:
                    print "adding " + response.contact.name
                    response_export_data['contact_name'] = response.contact.name
                else:
                    response_export_data['contact_name'] = "N/A"
                if response.contact and response.contact.gender:
                    response_export_data['sex'] = response.contact.gender
                else:
                    response_export_data['sex'] = 'N/A'
                if response.contact and response.contact.default_connection:
                    response_export_data['mobile']=response.contact.default_connection.identity
                else:
                    response_export_data['mobile']="N/A"
                if response.contact and response.contact.birthdate:

                    response_export_data['age'] = (datetime.datetime.now() - response.contact.birthdate).days/365

                else:
                    response_export_data['age'] = 'N/A'
                if response.contact and response.contact.reporting_location:
                    response_export_data['district'] = response.contact.reporting_location.name
                else:
                    response_export_data['district'] = 'N/A'
                if response.contact and response.contact.village:
                    response_export_data['village'] = response.contact.village.name
                else:
                    response_export_data['village'] = 'N/A'
                if response.contact and response.contact.groups.count() > 0:
                    response_export_data['groups'] = ",".join([group.name for group in response.contact.groups.all\
                        ()])
                else:
                    response_export_data['groups'] = 'N/A'
                if response.message:
                    response_export_data['response']=response.message.text
                    response_export_data['date']=response.message.date.date()
                    response_export_data['time']=response.message.date.time()

                else:
                    response_export_data['response']=''
                    response_export_data['date']=''
                    response_export_data['time']=''
                if response.poll:
                    response_export_data['question']=response.poll.question
                else:
                    response_export_data['question']=''



                response_data_list.append(response_export_data)
            ExcelResponse(response_data_list,output_name=excel_file_path,write_to_file=True)


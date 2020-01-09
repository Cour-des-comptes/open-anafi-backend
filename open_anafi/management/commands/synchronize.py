import random
import sys
import time

from django.core.management.base import BaseCommand

from open_anafi.models import Department, InstitutionType


class Command(BaseCommand):
    help = "Easter egg"

    def handle(self, *args, **options):
        self.stdout.write("Synchronizing open_anafi.Department...")
        time.sleep(1.5)
        for dep in Department.objects.all():
            self.stdout.write(f"Indexing {dep.number}")
            time.sleep(.1)
        time.sleep(0.5)
        self.stdout.write(self.style.SUCCESS("Done !"))
        time.sleep(0.5)
        self.stdout.write("Synchronizing open_anafi.InstitutionType...")
        time.sleep(1.5)
        for inst in InstitutionType.objects.all():
            self.stdout.write(f"Indexing {inst.number} - {inst.name}")
            time.sleep(.05)
        time.sleep(0.5)
        self.stdout.write(self.style.SUCCESS("Done !"))
        time.sleep(1)

        toolbar_width = 40
        self.stdout.write("Synchronizing data...")
        # setup toolbar
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        for i in range(toolbar_width):
            time.sleep(random.uniform(0.1, 0.4)) # do real work here
            # update the bar
            sys.stdout.write("█")
            sys.stdout.flush()

        sys.stdout.write("\n") 
        time.sleep(0.5)
        self.stdout.write(self.style.SUCCESS("Done !"))
        time.sleep(1.2)
        david = """
                                                                          
                                                                                
                                 ```````                                        
                       ``.-::::::::///:::::::-----..```                         
                    ``-/+syhhddddddddddddhhhhhhhhyysso+/-.`                     
                  `-/oyhdmNNNNNNNNNNNNNNNNNNNNNNNNNmmmdhys/-.`                  
                `-+shmmNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNmdyo/.                 
               `+hdmNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNmdy+`               
              .hmNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNmh.              
             .hNNNNNNNNNNNNNNNNNNNNNNNNNNNNmmmmdmmmNNNNNNNNNNNNNNd-`            
            .oMNNNNmmNNNmdyysoosyyyyysoosyso///://+syysyyyhdNNNNNMd-            
           `/NNNNmhyyhhys+//::----:::::-------------:::///+ohmNNMNMy-           
           -yMNNNdysssoo+//:::--------...------------:::////ymNNNNMm/           
          `+mNNNNdhsooo++//:::--------....-----------::::/:/smNNNNNMy-          
          .oNNNNNmhyo++++////::--------------------::::::::/sdNNNMNMm+          
          :hNNNNNmhyo+++++///::::------..-------:::::::::://shmNNNNNNs`         
          :hNNNNNdhyoo++++///::::-------.---------:::::::://+ydNNNNNNs`         
          -yNNNNNdyssoo+++//:::----...........------::::::///ohmmNNNNs`         
          -yNNNNmysssoo++////::---............-----::::::::///ohmmmNNo          
          :yMNNmhysssoyhsoo++/::----.........--:/++o+osso+/////+yNNNNs`         
          -sMNNhysyyhdNNNmmdddhhys+--------:+syhdmdmmmmNmmdy+////hNNNs`         
          .sMNNysshmNNNNmNNmmdhhyhhs:-::::/ohddhys+yhdddddddy+///hmmNs`         
          `omoosyhhhdmdyhdddhs+/osydy++//+os++ooooodhhysooo+sys+/+osy+--        
        .//+hdhhhhyyhyhmhydNNs/ssoohm+---:yy::+++/hmd+ohdo+:+sso/hNh+/os-       
        oossyNNysyysyyddhyyyo+++++ohh+:--:+h+///++/ooooooo+:--:::yNo::+o:       
        //+ohNNs+ossssysso++++////+oso/--:/+:::::://///////---:::ym+-://`       
        `:/+ohMs+++++o+//////::://++so/::://:---------------:::::+s/:::.        
          -+/:msooo+/::-------::/+ooso/::////::-......-----:::////::::-`        
          `-/-yhooo+//:::::--:::/+oyyo/:://+//::--...------::::///-:/:-         
           .///yyso++/:::::---::/oyys+:-::/++++/:---------:::::/+/--/:.         
           ./o:shso+//::::-----/ossys/-.-:/+++++/---------:::::/+/:-/:`         
           `:o:+hyoo++/:::::--:/syssdy+//+sysso+::------::::::///::/:.          
           `-o//yysso+//:::::://+ooosssoo++++o+/:::--::::::////+:-::.`          
            `-+/oysoso///////+oooooo+///////++++///:::::::://:/o. `             
              ```.oyoo//+++ossyyso++/:--:::::/+++o+///::::::::/+`               
                 `/ys+///++ossssoo++///:::::::////++///::-:::/++`               
                  .oh+/////++syhhhyysooo+++++oosyyyo///:-::::/+yy/.`            
                   -yy++//:///+osyyyssoo+++oooooo+/:::::://:/++omNdy/--..  ```  
                   `:msoo++/:///+osso++/////++//::---::///:/ooo+smNNNmmddysyys+/
                  `:hNhysooo/////+++++oooo+//:::-----:///:/sso++++dNNNNNNNNmmmmm
                 .omNMmdyssss+////////+oo++:::------://///sho//+o++hdmNNNNmmmmNN
                `smNmNNNmhysyo+////:::::::::--------://+oyy+/::/++:oyyhmmmmmmmmm
             ``.odNmmNNmNNmhhhs+++//+/::-::::-::::::/+osso/:::://+/osyhdmmmmmmmm
   `````````.-:smNmmNNNmhdNNmdhsooo++/:::::::::////+osso//::::::///oshdmmmmmmmmm
...-------:/oyhmmmmmmmNmdyydNNmhyoo+++/::::://///+oyyo+/:::::::://+sydmmmmmmmmmm
+ossyyhhhdmmmmmmmmmmmmmmdyo+shddhyo+++++++++++++oyhs+/:::::::://+osydmmmmmmmmmmm
dmmmmmmmmmmmmmmmmmmmmmmmdys+//+oooooooooooossssyso+//:::::://+oosyhdmmmmmmmmmmmm
mmmmmmmmmmmmmmmmmmmmmmmmdhso+///////////////++++//////////+osyyhddmmmmmmmmmmmmmm
mmmmmmmmmmmmmmmmmmmmmmmmmdhyysoo+++++//////////////++++oosyhddmmmmmmmmmmmmmmmmmm
mmmmmmmmmmmmmmmmmmmmmmmmmmmmdddhhhyyyysssssoooossssyyyhhddmmmmmmmmmmmmmmmmmmmmmm
mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmddddddddddddddmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
"""        
        self.stdout.write(self.style.SUCCESS(david))
        self.stdout.write(self.style.SUCCESS("""
        ❤~❤~❤~❤~❤~❤~❤~❤~❤~❤
       ❤~❤~❤ Merci David ❤~❤~❤
        ❤~❤~❤~❤~❤~❤~❤~❤~❤~❤
        """))


        

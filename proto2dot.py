"""
Generate graphviz dot files from *compiled* Google Protocol Buffer definitions

Python 2 compatible only

"""

import os
import sys
import logging
import importlib
import traceback
import StringIO
import copy
import re


from optparse import OptionParser

from google.protobuf import descriptor
from google.protobuf import reflection

__version__	= "1.0"
__author__	= "Laszlo Bako-Szabo"
__email__	= "lazics@gmail.com"
__license__	= "GPLv3"
__origin__  = "https://github.com/lazics/proto2dot" 

__edited_by__ = "Jozef Koczman"
__email_2__ = "jozino@gmail.com"


class Proto2Dot(object):
    output = None
    files = None
    messages = None

    def __init__(self, font_type,font_size,exclude, orientation):
        self.font_type = font_type
        self.font_size = font_size
        self.exclude = exclude
        self.orientation = orientation

        self.messages = {}
        self.output = {
            'nodes': {},
            'connections': [],
        }
        
        self.files = {}

        self.field_types_by_value={}

        for field_descr_n, field_descr_v in descriptor.FieldDescriptor.__dict__.iteritems():
            if not field_descr_n.startswith('TYPE_'):
                continue
            self.field_types_by_value[ field_descr_v ] = field_descr_n[ 5 : ].lower()

    def field_multiplicity(self, field):
        if field.label == field.LABEL_REQUIRED:
            return ("[1..1]", "required" )
        if field.label == field.LABEL_OPTIONAL:
            return ("[0..1]", "optional" )
        if field.label == field.LABEL_REPEATED:
            return ("[0..n]", "repeated" )
        raise Exception("Unknown field label")

    def check_port_side(self, field):
        if self.orientation == 'LR':
            self.port_on_left_side = False
        elif self.orientation == 'RL':
            self.port_on_left_side = True
        else:
            # logging.debug("field.name: %s", field.name)
            base_prev = re.match('^([^0-9]*([0-9]+[^0-9]+)*)[0-9]*$', self.prev_field_name).group(1)
            m = re.match('^([^0-9]*([0-9]+[^0-9]+)*)[0-9]*$', field.name)
            base_cur = m.group(1)
            if base_prev != base_cur:
                self.port_on_left_side = not self.port_on_left_side
            self.prev_field_name = field.name

    def is_excluded(self, name):
        if self.exclude:
            for p in self.exclude:
                # if ( re.match( ".*"+name+".*", p, re.IGNORECASE ) is not None ):
                if ( name in p ):
                    return True
        return False

    def process_message_class(self, message):
        if self.is_excluded(message.name):
            logging.info("Excluding whole message: %s" % (message.name, ) )
            return

        logging.debug("processing message %s" % (message.name,))

        self.messages[ message.name ] = message

        self.output["nodes"][ message.name ]="""
    %(name)s [
        shape = plaintext
        label = """ % {"name": message.name,}

        self.output["nodes"][ message.name ]+="<<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" ALIGN=\"LEFT\" VALIGN=\"TOP\"><TR><TD COLSPAN=\"4\"><B>"+ message.name +"</B></TD></TR>"

        self.prev_field_name = ''
        self.port_on_left_side = True
        for field in message.fields:

            if self.is_excluded(field.name):
                logging.info("field '%s->%s' excluded" % (message.name, field.name, ) )
                continue

            self.check_port_side( field )
            # reference to another message
            if field.type == field.TYPE_MESSAGE:
                port_left = "L_{}".format(field.name)
                port_left_tag = ' PORT="{}"' .format(port_left)
                port_right = "R_{}".format(field.name)
                port_right_tag = ' PORT="{}"' .format(port_right)
                port = port_left if self.port_on_left_side else port_right

                if not self.is_excluded(field.message_type.name):
                    self.output["connections"].append( "\t\t"+ message.name +":"+ port + " -> " + field.message_type.name )
                    logging.debug("Creating connection to {}".format(field.message_type.name) )
                else:
                    logging.info("Excluding Connection: {} -> {}".format(message.name, field.message_type.name) )
            else:
                port_left_tag = ""
                port_right_tag = ""

            self.output["nodes"][ message.name ] += "<TR>"

            # field number
            self.output["nodes"][ message.name ] += ("<TD %s>" % (port_left_tag, ) )+ str(field.number) +"</TD>" 

            # field multiplicity
            mult, label = self.field_multiplicity( field )
            
            self.output["nodes"][ message.name ] += "<TD TITLE=\""+ label +"\">" + mult + "</TD>"

            # field type
            self.output["nodes"][ message.name ] +=	"<TD ALIGN=\"LEFT\"><FONT COLOR=\"#444444\">&lt;" + self.field_types_by_value[ field.type ] + "&gt;</FONT></TD>"

            # field name with connection port
            self.output["nodes"][ message.name ] +=	"<TD ALIGN=\"LEFT\" %s>" % ( port_right_tag, )


            if field.type == field.TYPE_ENUM:
                # enum field, display a list of values
                self.output["nodes"][ message.name ] += "<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"0\"  ALIGN=\"LEFT\" VALIGN=\"TOP\"><TR><TD COLSPAN=\"3\" ALIGN=\"LEFT\">"+ field.name +"</TD></TR>"
                for e in field.enum_type.values:
                    self.output["nodes"][ message.name ] += "<TR><TD WIDTH=\"10\"></TD><TD ALIGN=\"LEFT\"><FONT POINT-SIZE=\""+ str(self.font_size - 2) +"\">["+ str(e.number) +"]</FONT></TD><TD ALIGN=\"LEFT\"><I><FONT POINT-SIZE=\""+ str(self.font_size - 2) +"\">"+ e.name +"</FONT></I></TD></TR>"
                self.output["nodes"][ message.name ] += "</TABLE>"
            else:
                # not an enum, just display the name
                self.output["nodes"][ message.name ] += field.name
            self.output["nodes"][ message.name ] += "</TD>"


            self.output["nodes"][ message.name ] += "</TR>"


        self.output["nodes"][ message.name ]+="</TABLE>>"

        self.output["nodes"][ message.name ]+="\n    ]\n"

    def process_py(self, filename):
        module_name = os.path.splitext( filename )[0]
        logging.debug("loading module '%s'..." % (module_name,))
        m = importlib.import_module( module_name )
        try:
            for message in m.DESCRIPTOR.message_types_by_name.itervalues():
                self.process_message_class( message )
        except:
            logging.error("Error processing '%s', skipping: \n%s" % (module_name, traceback.format_exc(),))


    def generate_dot_graph(self):
        f = StringIO.StringIO()
        header = """
digraph protobuf {
    rankdir=%(orientation)s
    fontname = "%(font_type)s"
    fontsize = %(font_size)s
    node [
        shape = record
        fontname = "%(font_type)s"
        fontsize = %(font_size)s
    ]
    edge [
        fontname = "%(font_type)s"
        fontsize = %(font_size)s
        arrowhead = "empty"
    ]
""" % {
    "font_type": self.font_type,
    "font_size": self.font_size,
    "orientation": self.orientation,
}
        f.write(header)
        f.write( '\n'.join(self.output["nodes"].values()) )
        f.write( '\n'.join(self.output["connections"]) )

        f.write("}")
        graph = f.getvalue()
        f.close()

        return graph

def main():

    parser = OptionParser()
    parser.usage = "%prog [options] <compiled proto files *.py>"

    parser.add_option( "-r", "--orientation", dest="orientation", help="Orientation of graph: TD = Top -> Down, LR = Left -> Right", type="string", default="LR")
    parser.add_option( "-f", "--font", dest="font_type", help="Font type", type="string", default="Bitstream Vera Sans" )
    parser.add_option( "--font-size", dest="font_size", help="Font size", type="int", default=9 )
    parser.add_option( "-x", "--exclude", dest="exclude", help="Exclude field/message names matching the specified regexp pattern", type="string", action="append")

    parser.add_option( "-d", "--debug", dest="debug", help="Print debug info", action="store_true", default=False)
    parser.add_option( "-o", "--output", dest="output", help="Output directory", type="string", default="." )

    for option in parser.option_list:
        if option.default != ("NO", "DEFAULT"):
            option.help += (" " if option.help else "") + "[default: %default]"

    (options, args) = parser.parse_args()
    log_format = '%(levelname)s: %(message)s'
    logging.basicConfig(level = logging.DEBUG if options.debug else logging.INFO, format=log_format)

    if len(args) == 0:
        parser.print_help()
        exit(0)

    logging.debug(options)
    

    
    o = Proto2Dot(
        font_type=options.font_type, 
        font_size=options.font_size,
        exclude=options.exclude, 
        orientation=options.orientation
        )

    for filename in args:
        logging.info("Processing file {}".format(filename))
        o.process_py(filename)

    # Generate graphviz .dot file
    graph = o.generate_dot_graph()

    dot_filename = filename + '.dot'

    logging.info("Saving dot file to '%s'..." % (dot_filename,))
    f = open(dot_filename, "wb")
    f.write( graph )
    f.close()

    return 0


if __name__ == "__main__":
    sys.exit( main() )

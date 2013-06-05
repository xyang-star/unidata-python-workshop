import xml.etree.ElementTree as ET
import urllib2
from urlparse import urlparse

# TODO: make more robust, check for nulls

xmlns_prefix = "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}"

def get_url_path(url):
    o = urlparse(url)
    parts = o.path.split('/')
    return o.scheme + "://" + o.netloc + '/'.join(parts[:-1])

def get_element_root_from_url(url):
    data = urllib2.urlopen(url)
    root = ET.parse(data).getroot()
    data.close()
    return root

def find_dataset(root, service_name):
    for ds in root.findall(xmlns_prefix + 'dataset'):
	sn = ds.find(xmlns_prefix + "serviceName")
	if ((sn is not None) and (service_name == sn.text)):
	    return ds
	else:
	    if find_dataset(ds, service_name) is not None:
		return find_dataset(ds, service_name)

def get_resolver_xml_url(dataset_url):
    root = get_element_root_from_url(dataset_url)
    latest = ''
    latest_base = ''
    latest_url = ''
    for s in root.findall(xmlns_prefix + 'service'):
    	if (s.get("serviceType") == "Resolver"):
	   latest = s.get("name")
    	   latest_base = s.get("base")
    ds = find_dataset(root,latest)
    # TODO: generalize this to handle relatives paths starting with a '/'	   
    latest_url = get_url_path(dataset_url) + latest_base + '/' + ds.get('urlPath')
    return latest_url

def get_service_endpoint(root, service):
    #TODO: Deal with suffix
    service_dict = {}
    for s in root.findall(xmlns_prefix + 'service'):
    	if (s.get("serviceType") == "Compound"):
	   for child in s:
	       service_dict[child.get("serviceType")] = child.get("base")
    return service_dict[service]


def get_latest_dods_url(dataset_url):
    o = urlparse(dataset_url)
    root = get_element_root_from_url(get_resolver_xml_url(dataset_url))
    ds = root.find(xmlns_prefix + 'dataset')
    return "http://" + o.netloc + get_service_endpoint(root,'OPENDAP') + ds.get('urlPath')

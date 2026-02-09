import os
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime


def prettify_xml(element: ET.Element) -> str:
    rough_string = ET.tostring(element, encoding="utf-8")
    dom = xml.dom.minidom.parseString(rough_string)
    pretty_xml = dom.toprettyxml(indent="  ")
    return "\n".join([line for line in pretty_xml.splitlines() if line.strip()])


class DataciteExportXML:
    @staticmethod
    def export_oai_aire(records, output_dir, filename=None):
        os.makedirs(output_dir, exist_ok=True)
        exported_files = []

        for record in records:
            print(record)
            record_el = ET.Element("record")
            header_el = ET.SubElement(record_el, "header")

            collection_name = ""
            for r in record.get("relatedIdentifiers", []):
                if (
                    r.get("relatedIdentifierType") == "Local"
                    and r.get("relationType") == "IsPartOf"
                ):
                    collection_name = r.get("relatedIdentifier")
                    break

            if "titles" in record and isinstance(record["titles"], list) and record["titles"]:
                 title = record["titles"][0].get("title", "unknown")

            ET.SubElement(header_el, "identifier").text = f"oai:{collection_name}:{title}"

            ET.SubElement(header_el, "datestamp").text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            
            ET.SubElement(header_el, "setSpec").text = "dataset"

            metadata_el = ET.SubElement(record_el, "metadata")

            oaire_ns = {
                "xmlns:oaire": "http://namespace.openaire.eu/schema/oaire/",
                "xmlns:datacite": "http://datacite.org/schema/kernel-4",
                "xmlns:dc": "http://purl.org/dc/elements/1.1/",
                "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://namespace.openaire.eu/schema/oaire/ https://www.openaire.eu/schema/repo-lit/4.0/openaire.xsd"
            }

            oaire_res = ET.SubElement(metadata_el, "oaire:resource", oaire_ns)

            if "identifier" in record:
                ident = record["identifier"]
                ET.SubElement(oaire_res, "datacite:identifier", {
                    "identifierType": ident.get("identifierType", "URL")
                }).text = ident.get("identifier")

            if "titles" in record:
                for t in record["titles"]:
                    ET.SubElement(oaire_res, "datacite:title").text = t.get("title")

            if "creators" in record:
                creators_el = ET.SubElement(oaire_res, "datacite:creators")
                for c in record["creators"]:
                    creator_el = ET.SubElement(creators_el, "datacite:creator")
                    ET.SubElement(creator_el, "datacite:creatorName").text = c.get("creatorName", "Unknown")
                    if "affiliation" in c:
                        ET.SubElement(creator_el, "datacite:affiliation").text = c["affiliation"]

            if "dates" in record:
                dates_el = ET.SubElement(oaire_res, "datacite:dates")
                for d in record["dates"]:
                    date_el = ET.SubElement(dates_el, "datacite:date", {
                        "dateType": d.get("dateType", "Issued")
                    })
                    date_el.text = d.get("date")

            if "publisher" in record:
                ET.SubElement(oaire_res, "dc:publisher").text = record["publisher"]
            
            if "contributor" in record:
                ET.SubElement(oaire_res, "datacite:contributor").text = record["contributor"]

            if "publicationYear" in record:
                ET.SubElement(oaire_res, "datacite:publicationYear").text = str(record["publicationYear"])

            if "language" in record:
                ET.SubElement(oaire_res, "dc:language").text = record["language"]

            if "descriptions" in record:
                for desc in record["descriptions"]:
                    ET.SubElement(oaire_res, "dc:description").text = desc.get("description")

            if "subjects" in record:
                for s in record["subjects"]:
                    ET.SubElement(oaire_res, "datacite:subject").text = s.get("subject")

            if "relatedIdentifiers" in record and record["relatedIdentifiers"]:
                first_r = record["relatedIdentifiers"][0]

                url = first_r.get("relatedIdentifier")
                alt_el = ET.SubElement(oaire_res, "datacite:alternateIdentifiers")
                alt_id = ET.SubElement(
                    alt_el,
                    "datacite:alternateIdentifier",
                    {"alternateIdentifierType": "URL"}
                )
                alt_id.text = url


            if "resourceType" in record:
                ET.SubElement(
                    oaire_res,
                    "oaire:resourceType",
                    {
                        "resourceTypeGeneral": record["resourceType"].get("resourceTypeGeneral", "dataset"),
                        "uri": record["resourceType"].get("uri", "http://purl.org/coar/resource_type/c_ddb1")
                    }
                ).text = record["resourceType"].get("resourceType", "")

            if "license" in record:
                ET.SubElement(
                    oaire_res,
                    "oaire:licenseCondition",
                    {
                        "uri": "https://creativecommons.org/licenses/by-sa/4.0"
                    }
                ).text = record["license"]

            if "formats" in record:
                for f in record["formats"]:
                    ET.SubElement(oaire_res, "dc:format").text = f

            if "rightsList" in record:
                rights = record["rightsList"]
                ET.SubElement(
                    oaire_res,
                    "datacite:rights",
                    {"rightsURI": rights.get("rightsURI", "")}
                ).text = rights.get("rights", "")



            if "geoLocations" in record:
                geos_el = ET.SubElement(oaire_res, "datacite:geoLocations")
                for g in record["geoLocations"]:
                    geo_el = ET.SubElement(geos_el, "datacite:geoLocation")
                    if "geoLocationPlace" in g:
                        ET.SubElement(geo_el, "datacite:geoLocationPlace").text = g["geoLocationPlace"]
                    if "geoLocationBox" in g:
                        box = g["geoLocationBox"]
                        box_el = ET.SubElement(geo_el, "datacite:geoLocationBox")
                        ET.SubElement(box_el, "datacite:westBoundLongitude").text = str(box.get("westBoundLongitude", ""))
                        ET.SubElement(box_el, "datacite:eastBoundLongitude").text = str(box.get("eastBoundLongitude", ""))
                        ET.SubElement(box_el, "datacite:southBoundLatitude").text = str(box.get("southBoundLatitude", ""))
                        ET.SubElement(box_el, "datacite:northBoundLatitude").text = str(box.get("northBoundLatitude", ""))
            
            if "fundingReferences" in record:
                fundrefs_el = ET.SubElement(oaire_res, "oaire:fundingReferences")
                for f in record["fundingReferences"]:
                    fund_el = ET.SubElement(fundrefs_el, "oaire:fundingReference")

                    if "funderName" in f:
                        ET.SubElement(fund_el, "oaire:funderName").text = f["funderName"]

                    if "funderIdentifier" in f:
                        ET.SubElement(fund_el, "oaire:funderIdentifier", {
                            "funderIdentifierType": f.get("funderIdentifierType", "")
                        }).text = f["funderIdentifier"]

                    if "fundingStream" in f:
                        ET.SubElement(fund_el, "oaire:fundingStream").text = f["fundingStream"]

                    if "awardNumber" in f:
                        award = f["awardNumber"]
                        if isinstance(award, dict):
                            ET.SubElement(fund_el, "oaire:awardNumber", {
                                "awardURI": award.get("awardURI", "")
                            }).text = award.get("awardNumber", "")
                        else:
                            ET.SubElement(fund_el, "oaire:awardNumber").text = str(award)

                    if "awardTitle" in f:
                        ET.SubElement(fund_el, "oaire:awardTitle").text = f["awardTitle"]

            
         
            if "version" in record:
                version = record["version"]
                ET.SubElement(
                    oaire_res, 
                    "oaire:version",
                    {"uri":version.get("uri","http://purl.org/coar/version/c_970fb48d4fbd8a85")}
                    ).text = version.get("version","VoR")

            title_for_filename = (
                record.get("titles", [{}])[0].get("title", "untitled")
                if isinstance(record.get("titles"), list)
                else "untitled"
            )
            file_name = filename or f"{title_for_filename.replace('.', '_')}.xml"
            filepath = os.path.join(output_dir, file_name)

            pretty_xml = prettify_xml(record_el)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(pretty_xml)

            exported_files.append(filepath)
            print(f"Exported {filepath}")

        return exported_files
    @staticmethod
    def export_datacite_v4(records, output_dir, filename=None):
        os.makedirs(output_dir, exist_ok=True)
        exported_files = []

        for record in records:
            ns = {
                "xmlns": "http://datacite.org/schema/kernel-4",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://datacite.org/schema/kernel-4 "
                                      "http://schema.datacite.org/meta/kernel-4.5/metadata.xsd"
            }
            root = ET.Element("resource", ns)

            if "identifier" in record:
                ident = record["identifier"]
                ET.SubElement(root, "identifier", {
                    "identifierType": ident.get("identifierType", "Local")
                }).text = ident.get("identifier")

            if "creators" in record:
                creators = ET.SubElement(root, "creators")
                for c in record["creators"]:
                    creator = ET.SubElement(creators, "creator")
                    ET.SubElement(creator, "creatorName").text = c.get("creatorName", "Unknown")

            if "titles" in record:
                titles = ET.SubElement(root, "titles")
                if isinstance(record["titles"], list):
                    for t in record["titles"]:
                        title_el = ET.SubElement(titles, "title")
                        title_el.text = t.get("title", "Untitled")
                else:
                    title = ET.SubElement(titles, "title")
                    title.text = str(record["titles"])

            publisher = ET.SubElement(root, "publisher")
            publisher.text = record.get("publisher", "Unknown")

            pub_year = record.get("publicationYear")
            if pub_year:
                ET.SubElement(root, "publicationYear").text = str(pub_year)

            if "subjects" in record:
                subjects = ET.SubElement(root, "subjects")
                for s in record["subjects"]:
                    ET.SubElement(subjects, "subject").text = s.get("subject")

            if "dates" in record:
                dates = ET.SubElement(root, "dates")
                for d in record["dates"]:
                    date_el = ET.SubElement(dates, "date", {
                        "dateType": d.get("dateType", "Issued")
                    })
                    date_el.text = d.get("date")

            if "language" in record:
                ET.SubElement(root, "language").text = record["language"]
            
            if "resourceType" in record:
                rt = record["resourceType"]
                ET.SubElement(root, "resourceType", {
                    "resourceTypeGeneral": rt.get("resourceTypeGeneral", "Dataset")
                }).text = rt.get("resourceType")
            
            if "alternateIdentifiers" in record:
                alt_ids = ET.SubElement(root, "alternateIdentifiers")
                for a in record["alternateIdentifiers"]:
                    alt_el = ET.SubElement(alt_ids, "alternateIdentifier", {
                        "alternateIdentifierType": a.get("alternateIdentifierType", "Local")
                    })
                    alt_el.text = a.get("alternateIdentifier")        

            if "descriptions" in record:
                descriptions = ET.SubElement(root, "descriptions")
                for d in record["descriptions"]:
                    desc = ET.SubElement(descriptions, "description", {
                        "descriptionType": d.get("descriptionType", "Abstract")
                    })
                    desc.text = d.get("description")

            if "geoLocations" in record:
                geos = ET.SubElement(root, "geoLocations")
                for g in record["geoLocations"]:
                    geo = ET.SubElement(geos, "geoLocation")
                    if "geoLocationBox" in g:
                        box = g["geoLocationBox"]
                        ET.SubElement(geo, "geoLocationBox", {
                            "westBoundLongitude": str(box["westBoundLongitude"]),
                            "eastBoundLongitude": str(box["eastBoundLongitude"]),
                            "southBoundLatitude": str(box["southBoundLatitude"]),
                            "northBoundLatitude": str(box["northBoundLatitude"])
                        })

            if "relatedIdentifiers" in record:
                relateds = ET.SubElement(root, "relatedIdentifiers")
                for r in record["relatedIdentifiers"]:
                    rel = ET.SubElement(relateds, "relatedIdentifier", {
                        "relatedIdentifierType": r.get("relatedIdentifierType", "URL"),
                        "relationType": r.get("relationType", "Related")
                    })
                    rel.text = r.get("relatedIdentifier")
            
            if "hasParts" in record:
                relateds = root.find("relatedIdentifiers") or ET.SubElement(root, "relatedIdentifiers")
                for part in record["hasParts"]:
                    rel = ET.SubElement(relateds, "relatedIdentifier", {
                        "relatedIdentifierType": "Local",
                        "relationType": "HasPart"
                    })
                    rel.text = part

            if "isPartOf" in record:
                relateds = root.find("relatedIdentifiers") or ET.SubElement(root, "relatedIdentifiers")
                rel = ET.SubElement(relateds, "relatedIdentifier", {
                    "relatedIdentifierType": "Local",
                    "relationType": "IsPartOf"
                })
                rel.text = record["isPartOf"]

            if "version" in record:
                ET.SubElement(root, "version").text = record["version"]
            
            if "rightsList" in record:
                rights_el = ET.SubElement(root, "rightsList")
                for r in record["rightsList"]:
                    attrs = {}
                    if r.get("rightsURI"):
                        attrs["rightsURI"] = r["rightsURI"]
                    right = ET.SubElement(rights_el, "rights", attrs)
                    right.text = r.get("rights")
           
            if "formats" in record:
                formats = ET.SubElement(root, "formats")
                for f in record["formats"]:
                    ET.SubElement(formats, "format").text = f        
           
            title_for_filename = "untitled"
            if "titles" in record:
                if isinstance(record["titles"], list) and record["titles"]:
                    title_for_filename = record["titles"][0].get("title", "untitled")
                elif isinstance(record["titles"], str):
                    title_for_filename = record["titles"]

            file_name = filename or f"{title_for_filename.replace('.', '_')}.xml"
            filepath = os.path.join(output_dir, file_name)
            
            pretty_xml = prettify_xml(root)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(pretty_xml)

            exported_files.append(filepath)
            print(f"Exported {filepath}")

        return exported_files

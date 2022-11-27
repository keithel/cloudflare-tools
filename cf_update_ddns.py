#!/usr/bin/env python3
import requests
import argparse
import os

import CloudFlare

def public_ip():
    url = "https://api.ipify.org"
    try:
        ip = requests.get(url).text
    except:
        exit(f"{url}: failed")
    if ip == "":
        exit(f"{url}: failed")
    if ":" in ip:
        address_type = "AAAA"
    else:
        address_type = "A"
    return ip, address_type

def get_zone_record(cf, zone_id, dns_name, ip_type):
    try:
        params = {
            "name": dns_name,
            "match": "all",
            "type": ip_type
        }
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit(f"/zones/dns_records {dns_name} - {int(e)} {str(e)} - api call failed")

    if len(dns_records) > 1:
        ips = [record["content"] for record in dns_records]
        print(f"{len(dns_records)} records found for {dns_name} {ip_type}: {str(ips)}")
        exit(f"too many dns records for {dns_name} {ip_type}")
    elif len(dns_records) < 1:
        exit(f"No records found for {dns_name} {ip_type}")

    for dns_record in dns_records:
        record_id = dns_record["id"]
        ip = dns_record["content"]
        proxied_state = dns_record["proxied"]

    return record_id, ip, proxied_state

def do_dns_update(cf, zone_id, dns_name, ip, ip_type):
    dns_record_id, old_ip, proxied_state = get_zone_record(cf, zone_id, dns_name, ip_type)

    if ip == old_ip:
        print(f"Nothing to do, IP address is unchanged: {dns_name} {ip}")
        return

    # We're good to update this record
    dns_record = {
        "name": dns_name,
        "type": ip_type,
        "content": ip,
        "proxied": proxied_state
    }

    try:
        dns_record = cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit(f"/zones/dns_records.post {dns_name} - {int(e)} {str(e)} - api call failed")
    print(f"SET: {dns_name} {ip}")

    _, new_ip, _ = get_zone_record(cf, zone_id, dns_name, ip_type)
    if ip != new_ip:
        exit(f"Failed to set {dns_name} {ip}")

    print(f"VERIFIED: {dns_name} {ip}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dns_name", metavar="fqdn-hostname", type=str, help="The DNS name to update")
    args = parser.parse_args()
    print(f"dns-name: {args.dns_name}")
    dns_name = args.dns_name

    host_name, zone_name = ".".join(dns_name.split(".")[:2]), ".".join(dns_name.split(".")[-2:])
    print(f"host_name, zone_name: {host_name}, {zone_name}")

    ip, ip_type = public_ip()
    print(f"MY IP: {ip}")

    token = os.getenv("CF_TOKEN")
    if token is None:
        try:
            with open("cf.token") as f:
                token = f.readline().strip()
        except FileNotFoundError as e:
            exit(f"CF_TOKEN env var not set, and {os.getcwd()}/cf.token file not found\nNo way to authenticate with cloudflare.")
        except IOError as e:
            exit(f"Error reading {os.getcwd()}/cf.token file\nNo way to authenticate with cloudflare.")

    cf = CloudFlare.CloudFlare(token=token)
    try:
        params = { "name": zone_name }
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit(f"/zones {int(e)} {str(e)} - api call failed")
    except Exception as e:
        exit(f"/zones.get - {e} - api call failed")

    if len(zones) == 0:
        exit(f"zones.get - {zone_name} - zone not found")
    elif len(zones) != 1:
        exit(f"zones.get - {zone_name} - api call returned {len(zones)} items")

    zone = zones[0]
    zone_name = zone["name"]
    zone_id = zone["id"]

    do_dns_update(cf, zone_id, dns_name, ip, ip_type)

if __name__ == '__main__':
    main()

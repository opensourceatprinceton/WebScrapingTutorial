from lxml import etree
import requests
import json


class Submissions(object):

	def __init__(self):
		self.base_url = 'http://hackprincetons2016.devpost.com'
		# Main url to get the page
		main_url = '/submissions'

		# Find the number of pages of submissions
		print("[INFO] Getting the number of submission pages:"),
		submission_pages = self.get_submission_pages(main_url)
		print("%d pages found." % (len(submission_pages)))
		
		# Get the submissions for each page
		self.submissions = []
		for i in range(len(submission_pages)):
			print("[INFO] Getting submissions from page %s" % (submission_pages[i][0]))
			self.submissions.extend(self.get_submissions_from_page(submission_pages[i][1]))

		print("[INFO] %d total submissions." % (len(self.submissions)))

	def _get_body(self, main_url):
		print("[GET] Getting body of %s%s" % (self.base_url, main_url))
		page = requests.get(self.base_url + main_url)
	
		# If incorrect status code, print error
		if(page.status_code != 200):
			print("[ERROR] Could not GET %s. Return code = %d." % (self.base_url + main_url, page.status_code))
			print("[ERROR] %s" % (page.content))

		# Make the html code parsable using the lxml library
		html = etree.HTML(page.content)

		return html

	def _create_submission(self, submission_element):
		# Find the url, name, tagline, authors, winner
		url = submission_element[0].attrib['href']
		name = submission_element.find('.//h5').text.strip()
		tagline = submission_element.find('.//p[@class="small tagline"]').text.strip()
		authors = [img.attrib['title'] for img in submission_element.findall(".//span[@class='user-profile-link']/img")]
		winner = submission_element.find('.//aside[@class="entry-badge"]') is not None

		submission = {
			'Winner': winner,
			'Name': name,
			'Tagline': tagline,
			'Authors': authors,
			'URL': url
		}

		return submission

	def get_submission_pages(self, main_url):
		pages = []

		# Perform GET request to get the body of the html code of the page
		body = self._get_body(main_url)

		# Find the element that corresponds to the pagination of the page
		pagination = body.find('.//ul[@class="pagination"]')

		# Get a list of 'li' elements. The first element of each has an 'href' attrib
		# that corresponds to the url needed to get the page
		for li_element in pagination[1:-1]:
			pages.append((li_element[0].text, li_element[0].attrib['href']))

		return pages


	def get_submissions_from_page(self, page_url):
		# Get body of page
		body = self._get_body(page_url)

		# Find the elements that correspond to the submissions.
		# Can be found with div elements that have attrib 'software-id'
		submission_elements = body.findall('.//div[@data-software-id]')

		submissions = [self._create_submission(submission_element) for submission_element in submission_elements]

		return submissions

	def toJSON(self, filename):
		# assume filename is a json file
		print("[WRITING] Writing to json file: %s" % filename)
		with open(filename, "w") as fw:
			fw.write(json.dumps(self.submissions, indent=2, sort_keys=True))


def main():
	subs = Submissions()
	subs.toJSON("submissions.json")


if __name__ == '__main__':
	main()
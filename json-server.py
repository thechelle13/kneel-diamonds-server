import json
from http.server import HTTPServer
from nss_handler import HandleRequests, status

# Add your imports below this line
from src import MetalView, SizeView, StyleView, OrderView


class JSONServer(HandleRequests):

    def do_GET(self):
        url = self.parse_url(self.path)
        view = self.determine_view(url)
        expand_param = url["query_params"].get("_expand")

        self.expand_response(url, view, expand_param)


    def do_PUT(self):
        url = self.parse_url(self.path)
        view = self.determine_view(url)

        try:
            view.update(self, self.get_request_body(), url["pk"])
        except AttributeError:
            return self.response("No view for that route", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)

    def do_POST(self):
        # Parse the URL
        url = self.parse_url(self.path)
        # Determine the correct view needed to handle the requests
        view = self.determine_view(url)
        # Get the request body
        # Invoke the correct method on the view
        # Make sure you handle the AttributeError in case the client requested a route that you don't support
        view.insert(self, self.get_request_body())
        
        # Once you implement this method, delete the following line of code
        # return self.response("", status.HTTP_405_UNSUPPORTED_METHOD.value)

    def do_DELETE(self):
        url = self.parse_url(self.path)
        view = self.determine_view(url)

        try:
            view.delete(self, url["pk"])
        except AttributeError:
            return self.response("No view for that route", status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value)


    def determine_view(self, url):
        """Lookup the correct view class to handle the requested route

        Args:
            url (dict): The URL dictionary

        Returns:
            Any: An instance of the matching view class
        """
        try:
            routes = {
                "metals": MetalView,
                "sizes": SizeView,
                "styles": StyleView,
                "orders": OrderView
            }

            matching_class = routes[url["requested_resource"]]
            return matching_class()
        except KeyError:
            return status.HTTP_404_CLIENT_ERROR_RESOURCE_NOT_FOUND.value

    def expand_response(self, url, view, expand_param):
        if expand_param is not None:
            response = view.get_expanded(self, url["pk"], expand_param)
        else:
            response = view.get(self, url["pk"])
        if response is not None:
            response = json.dumps(response)


#
# THE CODE BELOW THIS LINE IS NOT IMPORTANT FOR REACHING YOUR LEARNING OBJECTIVES
#
def main():
    host = ''
    port = 3000
    HTTPServer((host, port), JSONServer).serve_forever()

if __name__ == "__main__":
    main()
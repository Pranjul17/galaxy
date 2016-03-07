import json
from requests import post
import pprint

from base import api
# from .helpers import DatasetPopulator

import logging
log = logging.getLogger( "functional_tests.py" )


class ApiBatchTestCase( api.ApiTestCase ):

    def _get_api_key( self, admin=False ):
        return self.galaxy_interactor.api_key if not admin else self.galaxy_interactor.master_api_key

    def _with_key( self, url, admin=False ):
        return url + '?key=' + self._get_api_key( admin=admin )

    def _post_batch( self, batch ):
        data = json.dumps({ "batch" : batch })
        return post( "%s/batch" % ( self.galaxy_interactor.api_url ), data=data )

    def log_reponse( self, response ):
        log.debug( 'RESPONSE %s\n%s', ( '-' * 40 ), pprint.pformat( response ) )

    def test_simple_array( self ):
        batch = [
            dict( url=self._with_key( '/api/histories' ) ),
            dict( url=self._with_key( '/api/histories' ),
                  method='POST', body=json.dumps( dict( name='Wat' ) ) ),
            dict( url=self._with_key( '/api/histories' ) ),
        ]
        response = self._post_batch( batch )
        response = response.json()
        # self.log_reponse( response )
        self.assertIsInstance( response, list )
        self.assertEquals( len( response ), 3 )

    def test_bad_route( self ):
        batch = [
            dict( url=self._with_key( '/api/bler' ) )
        ]
        response = self._post_batch( batch )
        response = response.json()
        # self.log_reponse( response )
        self.assertIsInstance( response, list )
        self.assertEquals( response[0][ 'status' ], 404 )

    def test_errors( self ):
        batch = [
            dict( url=self._with_key( '/api/histories/abc123' ) ),
            dict( url=self._with_key( '/api/users/123' ), method='PUT' ),
        ]
        response = self._post_batch( batch )
        response = response.json()
        # self.log_reponse( response )
        self.assertIsInstance( response, list )
        self.assertEquals( response[0][ 'status' ], 400 )
        self.assertEquals( response[1][ 'status' ], 501 )

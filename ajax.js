// Namespace.
var AJAX = {};

/**
 * Issues an AJAX request.
 * @param {String} actoin  The CGI script.
 * @param {Object} params   A map of name-value pairs.
 * @param {Function(String, Number)} callback  The function to call with the response.
 * @param {String} opt_method  "GET" or "POST".
 **/
AJAX.request = function( action, params, callback, opt_method )
{
    opt_method = opt_method || "GET";
    if( opt_method == "GET" )
        AJAX.downloadUrl( AJAX.createRequestUrl( action, params ), callback, opt_method );
    else
        AJAX.downloadUrl( action, callback, opt_method, AJAX.urlEscapeParams( params ) );
};

/**
 * Issues an AJAX request and expects JSON in return.
 * @param {String} action  The CGI script.
 * @param {Object} params  A map of name-value pairs.
 * @param {Function(Object, Number)}  The function to call with the response.
 * @param {String} opt_method  "GET" or "POST".
 **/
AJAX.jsonRequest = function( action, params, callback, opt_method )
{
    AJAX.request( action, params, function( body, code )
    {
        var response = null;
        if( body ) response = AJAX.parseJson( body );
        if( response ) callback( response, code );
        else callback( null, 503 );
    }, opt_method );
};

AJAX.parseJson = function( text )
{
    return eval("(" + text + ")");
};

/**
 * Downloads the contents of a page asynchronously.
 * @param {String} url  A URL, possibly with parameters.
 * @param {Function(String, Number)} callback  Called with the response text and HTTP code.
 * @param {String} opt_method  "GET" or "POST".
 * @param {String} opt_body  Request body.
 * @return {Boolean}  true on success.
 **/
AJAX.downloadUrl = function( url, callback, opt_method, opt_body )
{
    var request = AJAX.getXmlHttpRequest();
    if( !request ) return false;

    request.onreadystatechange = function()
    {
        if( request.readyState == 4 )
        {
            var response;
            var rstatus;
            try
            {
                response = request.responseText;
                rstatus = request.status;
            }
            catch( e )
            {
                response = null;
                rstatus = 503;
            }
            callback( response, rstatus );
        }
    };

    opt_method = opt_method ? opt_method : "GET";
    opt_body = opt_body ? opt_body : "";
    
    request.open( opt_method, url, true );
    if( opt_method == "POST" )
    {
        // Chrome doesn't like to send this.
        //request.setRequestHeader( "Content-Length", opt_body.length );
        request.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
    }

    request.send( opt_body );
    return true;
}

/**
 * Returns the XmlHttpRequest object appropriate for this browser.
 **/
AJAX.getXmlHttpRequest = function()
{
    try
    {
        if( typeof ActiveXObject != "undefined" ) return new ActiveXObject( "Microsoft.XMLHTTP" );
        if( window.XMLHttpRequest ) return new XMLHttpRequest();
    }
    catch( e )
    {
        return null;
    }
};

/**
 * Takes a map of name-value pairs and creates a request string.
 * @param {String} action  A path to a CGI script.
 * @param {Object} params  A name-value map.
 **/
AJAX.createRequestUrl = function( action, params )
{
    return action + "?" + AJAX.urlEscapeParams( params );
};

/**
 * Encodes a set of name-value pairs into a URL.
 * @param {Object} params  A name-value map.
 * @return {String}  A URL.
 **/
AJAX.urlEscapeParams = function( params )
{
    var pairs = [];
    for( var i in params )
        pairs.push( encodeURIComponent( i ) + "=" + encodeURIComponent( params[i] ) );
    return pairs.join( "&" );
};


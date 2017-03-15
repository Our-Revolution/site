vcl 4.0;

backend default {
    .host = "localhost:8000";
}

acl purge {
    "localhost";
    "172.31.43.226"/32;
    "172.31.14.45"/32;
    "172.31.14.44"/32;
    "172.31.14.43"/32;
    "172.31.14.46"/32;
}


sub vcl_recv {

    if (req.method == "PURGE") {
        if (!client.ip ~ purge) {
            return (synth(405, "Not allowed."));
        } else {
            return(purge);
        }
    }
}

sub vcl_recv {
    
    if (req.url !~ "^/admin/" && req.url !~ "^/cms/" && req.url !~ "^/groups/new/"){
        unset req.http.Cookie;
        unset req.http.Cache-Control;
    }
}

sub vcl_backend_response {
    if (bereq.uncacheable) {
        return (deliver);
    } else if (bereq.url !~ "^/admin/" && bereq.url !~ "^/cms/" && bereq.url !~ "^/groups/new/") {
        unset beresp.http.Set-Cookie;
        unset beresp.http.Cache-control;
        set beresp.ttl = 4h;
    } else if (beresp.ttl <= 0s ||
      beresp.http.Set-Cookie ||
      beresp.http.Surrogate-control ~ "no-store" ||
      (!beresp.http.Surrogate-Control &&
        beresp.http.Cache-Control ~ "no-cache|no-store|private") ||
      beresp.http.Vary == "*") {
        # Mark as "Hit-For-Pass" for the next 2 minutes
        set beresp.ttl = 120s;
        set beresp.uncacheable = true;
    }
    return (deliver);
}

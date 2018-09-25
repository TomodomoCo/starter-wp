<?php

namespace Tomodomo\Controllers;

class BaseController
{
    /**
     * @var \Pimple\Container
     */
    public $container;

    /**
     * @param \Pimple\Container $container
     *
     * @return void
     */
    public function __construct($container)
    {
        // Grab the Pimple container
        $this->container = $container;

        // Twig!
        $this->twig = $this->container['twig'];

        return;
    }
}
